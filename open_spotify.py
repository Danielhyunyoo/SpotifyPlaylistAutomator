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

# How long we're willing to poll for a device before giving up.
# Generous because a pending Spotify auto-update can take well past
# a normal cold start.
MAX_WAIT_SECONDS = 45

# How often we re-check for a device while waiting
POLL_INTERVAL_SECONDS = 1


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


def _wait_for_any_device(sp, timeout=MAX_WAIT_SECONDS):
    """
    Polls sp.devices() until at least one device shows up or we run
    out of time. This is what absorbs the extra delay when Spotify
    is installing an update before it can open, instead of just
    failing after a fixed short wait.
    """
    waited = 0.0

    while waited < timeout:
        devices = sp.devices()

        if devices["devices"]:
            return devices["devices"][0]

        time.sleep(POLL_INTERVAL_SECONDS)
        waited += POLL_INTERVAL_SECONDS

    return None


def spotify_running_checker(sp):
    """
    Ensures Spotify is open and has an active playback device.
    Returns True once ready to receive playback commands, False if
    we couldn't get there.
    """
    logger.info("Checking for active Spotify devices")

    active_device = _get_active_device(sp)

    if active_device:
        logger.info("Active device found")
        return True

    logger.info("No active device found")

    # Only launch Spotify if it isn't already running somewhere. If
    # it's running but just has no active device yet, we don't need
    # to relaunch it, just wake it below.
    if not _is_spotify_process_running():
        logger.info("Launching Spotify")

        try:
            os.startfile(SPOTIFY_EXE)
        except Exception as e:
            logger.error(f"Failed to open Spotify: {e}")
            return False

    # Poll instead of a fixed sleep. Covers both a normal cold start
    # and the slower case where Spotify updates itself before opening.
    logger.info("Waiting for Spotify to report a device")
    target_device = _wait_for_any_device(sp)

    if not target_device:
        logger.error("Timed out waiting for a Spotify device to appear")
        return False

    logger.info(f"Waking device: {target_device['name']}")

    try:
        # transfer_playback with force_play=False makes this device
        # the active one without starting any audio, so there's no
        # brief blip like the old start_playback + pause combo had
        sp.transfer_playback(device_id=target_device["id"], force_play=False)
        logger.info("Device activated")
        return True
    except Exception as e:
        logger.error(f"Couldn't activate device: {e}")
        logger.error("Play something in Spotify manually, then run again")
        return False
