"""
open_spotify.py

Makes sure the Spotify desktop client is running and has an active
playback device, launching it if necessary.

Uses polling instead of a fixed sleep so we only wait as long as we
actually have to. That matters most when Spotify happens to be
mid-update on launch: a fixed 3 second sleep used to just fail in
that case, while polling with a longer overall timeout rides it out.
"""

import os
import subprocess
import time

from logger_setup import get_logger

logger = get_logger(__name__)

# Path to the Spotify executable on this machine
SPOTIFY_EXE = r"C:\Users\Blest\AppData\Roaming\Spotify\Spotify.exe"

# The desktop app registers as this device type. We prefer it
# specifically, since other always-on Spotify Connect endpoints (a
# smart speaker, a phone with the app installed, etc.) can otherwise
# show up in the device list before the client we just launched
# does, and end up getting picked instead.
PREFERRED_DEVICE_TYPE = "Computer"

# How long we're willing to poll for a device before giving up.
# Generous because a pending Spotify auto-update can take well past
# a normal cold start.
MAX_WAIT_SECONDS = 45

# How often we re-check for a device while waiting. Short, since a
# quick poll interval is what makes this feel instant once Spotify
# actually is ready, at the cost of a bit more CPU while waiting.
POLL_INTERVAL_SECONDS = 0.5

# After this many seconds of the process being up but still no
# device, we log a heads-up that this is probably an update running,
# not just a slow launch. Purely informational, doesn't change
# behavior, just makes the log less confusing when you go check it.
UPDATE_SUSPECTED_AFTER_SECONDS = 8

# transfer_playback is asynchronous on Spotify's end. This is how
# long we're willing to wait for the device to actually report as
# active afterwards, before handing control back. Skipping this wait
# is what used to cause an immediate "NO_ACTIVE_DEVICE" error on the
# very next API call.
TRANSFER_CONFIRM_TIMEOUT_SECONDS = 5


def _is_spotify_process_running():
    """
    Quick check via tasklist so we can skip the launch step entirely
    when Spotify is already open somewhere. This is the single
    biggest speed win, since os.startfile + waiting is the slow path.
    """
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq Spotify.exe"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return "Spotify.exe" in result.stdout
    except Exception as e:
        logger.warning(f"Couldn't check running processes: {e}")
        return False


def _get_active_device(sp):
    """Returns the first active device, or None if there isn't one."""
    devices = sp.devices()
    active_devices = [d for d in devices["devices"] if d["is_active"]]
    return active_devices[0] if active_devices else None


def _get_active_computer_device(sp):
    """
    Returns the active device only if it's the desktop app
    specifically. A phone or smart speaker left "active" from an
    earlier session otherwise satisfies the naive "is anything
    active" check forever, since Spotify keeps reporting the last
    controlled device as active even when nothing is currently
    playing on it. Pressing the hotkey means we want the PC, so that
    stale state shouldn't count as "ready."
    """
    devices = sp.devices()["devices"]

    for device in devices:
        if device["is_active"] and device["type"] == PREFERRED_DEVICE_TYPE:
            return device

    return None


def _wait_for_device(sp, timeout=MAX_WAIT_SECONDS):
    """
    Polls sp.devices() until a usable device shows up, preferring a
    Computer-type device (the desktop app we just launched) over
    anything else. Falls back to the first device seen if a Computer
    device never turns up in time, rather than failing outright.

    Also logs a one-time heads-up if Spotify's process is already up
    but still hasn't produced a device after a few seconds, since
    that pattern is what an in-progress Spotify update looks like
    from the outside.
    """
    waited = 0.0
    warned_about_update = False
    fallback_device = None

    while waited < timeout:
        devices = sp.devices()["devices"]

        computer_device = next(
            (d for d in devices if d["type"] == PREFERRED_DEVICE_TYPE), None
        )

        if computer_device:
            return computer_device

        if devices and fallback_device is None:
            fallback_device = devices[0]

        if not warned_about_update and waited >= UPDATE_SUSPECTED_AFTER_SECONDS:
            if _is_spotify_process_running():
                logger.info(
                    f"Spotify is running but no device after {waited:.0f}s, "
                    "likely installing an update, still waiting"
                )
            warned_about_update = True

        time.sleep(POLL_INTERVAL_SECONDS)
        waited += POLL_INTERVAL_SECONDS

    if fallback_device:
        logger.warning(
            f"No Computer device showed up in time, falling back to "
            f"'{fallback_device['name']}'"
        )

    return fallback_device


def _wait_until_active(sp, timeout=TRANSFER_CONFIRM_TIMEOUT_SECONDS):
    """
    Polls until some device reports is_active, or we run out of
    time. Called right after transfer_playback, since that call
    returns before the transfer has actually finished on Spotify's
    side, and issuing another command too soon fails with
    NO_ACTIVE_DEVICE.
    """
    waited = 0.0

    while waited < timeout:
        if _get_active_device(sp):
            return True

        time.sleep(0.3)
        waited += 0.3

    return False


def spotify_running_checker(sp):
    """
    Ensures Spotify is open and has an active playback device.
    Returns True once ready to receive playback commands, False if
    we couldn't get there.
    """
    logger.info("Checking for active Spotify devices")

    active_device = _get_active_computer_device(sp)

    if active_device:
        logger.info("Active desktop device found")
        return True

    logger.info("No active desktop device found (may still be active on another device)")

    # Only launch Spotify if it isn't already running somewhere. If
    # it's running but just has no active device yet, we don't need
    # to relaunch it, just wake it below. This is the main speed win,
    # since skipping a redundant launch avoids Spotify's own startup
    # cost entirely.
    if not _is_spotify_process_running():
        logger.info("Launching Spotify")

        try:
            os.startfile(SPOTIFY_EXE)
        except Exception as e:
            logger.error(f"Failed to open Spotify: {e}")
            return False

    # Poll instead of a fixed sleep, and poll fast, so we grab a
    # device the instant it's available rather than always eating a
    # fixed delay. Also covers the case where Spotify updates itself
    # before opening, since we just keep waiting up to MAX_WAIT_SECONDS.
    logger.info("Waiting for Spotify to report a device")
    target_device = _wait_for_device(sp)

    if not target_device:
        logger.error("Timed out waiting for a Spotify device to appear")
        return False

    logger.info(f"Waking device: {target_device['name']}")

    try:
        # transfer_playback with force_play=False makes this device
        # the active one without starting any audio, so there's no
        # brief blip like the old start_playback + pause combo had
        sp.transfer_playback(device_id=target_device["id"], force_play=False)
    except Exception as e:
        logger.error(f"Couldn't activate device: {e}")
        logger.error("Play something in Spotify manually, then run again")
        return False

    # transfer_playback returns before the transfer is actually done.
    # Wait for it to land before handing control back, otherwise the
    # very next command (shuffle/start_playback) can fail with
    # NO_ACTIVE_DEVICE even though we "just" activated it.
    if not _wait_until_active(sp):
        logger.warning("Device transfer may not have finished in time")

    logger.info("Device activated")
    return True
