"""
playlist_automator.py

Entry point run by the AHK hotkey. Makes sure Spotify is open and
playing the main playlist on shuffle.

If the main playlist is already the active thing playing, the hotkey
doubles as a play/pause toggle instead of doing a full relaunch, so
the same key works whether you're starting fresh or just pausing.
"""

import os
import time

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

from open_spotify import spotify_running_checker
from logger_setup import get_logger

logger = get_logger(__name__)

# If you know your playlist's URI, paste it here to skip the
# lookup-by-name step (a bit faster, and immune to renames). Leave
# as None to always search by name. When found by name, the URI
# gets logged so you can copy it in here afterwards.
MAIN_PLAYLIST_URI = None
MAIN_PLAYLIST_NAME = "It's Raining After All"

# How many times to retry starting playback if Spotify's API says
# the device isn't active yet. Belt-and-suspenders on top of the
# wait already done in open_spotify.py, since this can still happen
# if Spotify is just being slow to sync device state.
PLAYBACK_RETRY_ATTEMPTS = 3
PLAYBACK_RETRY_DELAY_SECONDS = 1.5


def build_client():
    """
    Loads credentials from .env and builds an authenticated spotipy
    client. Raises a clear error instead of a confusing KeyError if
    .env is missing or incomplete.
    """
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    load_dotenv(dotenv_path=env_path)

    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8000/callback")

    if not client_id or not client_secret:
        logger.error("Missing SPOTIFY_CLIENT_ID / SPOTIFY_CLIENT_SECRET. Copy .env.example to .env and fill it in.")
        raise SystemExit(1)

    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="user-read-playback-state user-modify-playback-state playlist-read-private",
    )

    return spotipy.Spotify(auth_manager=auth_manager)


def find_main_playlist(sp):
    """
    Finds the main playlist, preferring a direct URI lookup (fast)
    and falling back to searching by name (slower, but resilient if
    the saved URI ever goes stale).
    """
    if MAIN_PLAYLIST_URI:
        try:
            playlist = sp.playlist(MAIN_PLAYLIST_URI)
            logger.info(f"Found '{playlist['name']}' by saved URI")
            return playlist
        except Exception as e:
            logger.warning(f"Saved playlist URI didn't resolve ({e}), falling back to name search")

    # 50 limit to ensure we grab ALL our playlists
    playlists = sp.current_user_playlists(limit=50)

    for playlist in playlists["items"]:
        if playlist["name"] == MAIN_PLAYLIST_NAME:
            logger.info(f"Found '{playlist['name']}' by name. URI: {playlist['uri']}")
            return playlist

    return None


def toggle_if_already_playing(sp, main_playlist_uri):
    """
    If the main playlist is already the active context on some
    device, just toggle play/pause instead of doing a full relaunch.
    Returns True if it handled things (caller should stop there),
    False if the normal launch-and-play flow should run instead.
    """
    try:
        playback = sp.current_playback()
    except Exception as e:
        logger.warning(f"Couldn't read current playback state: {e}")
        return False

    if not playback or not playback.get("device"):
        return False

    context = playback.get("context")
    is_our_playlist = context is not None and context.get("uri") == main_playlist_uri

    if not is_our_playlist:
        return False

    if playback["is_playing"]:
        sp.pause_playback()
        logger.info("Playlist was already playing, paused it")
    else:
        sp.start_playback()
        logger.info("Playlist was paused, resumed it")

    return True


def start_shuffled_playback(sp, playlist_uri):
    """
    Turns on shuffle and starts playback of the given playlist,
    retrying a few times if Spotify reports the device isn't active
    yet. This can happen even after open_spotify.py already waited
    for the transfer to land, since Spotify's device state can lag
    a bit further behind than that.
    """
    for attempt in range(1, PLAYBACK_RETRY_ATTEMPTS + 1):
        try:
            # Shuffle is turned on BEFORE playback starts. Doing it
            # the other way around (like the old version did) plays
            # track 1 for a beat before shuffle kicks in, this avoids
            # that.
            sp.shuffle(True)
            sp.start_playback(context_uri=playlist_uri)
            logger.info("Playlist is running")
            return True
        except Exception as e:
            logger.warning(f"Playback attempt {attempt}/{PLAYBACK_RETRY_ATTEMPTS} failed: {e}")

            if attempt < PLAYBACK_RETRY_ATTEMPTS:
                time.sleep(PLAYBACK_RETRY_DELAY_SECONDS)

    logger.error("Gave up starting playback after retries")
    return False


def main():
    sp = build_client()

    main_playlist = find_main_playlist(sp)

    if not main_playlist:
        logger.error("Couldn't find main playlist")
        return

    if toggle_if_already_playing(sp, main_playlist["uri"]):
        return

    if not spotify_running_checker(sp):
        logger.error("Failed to open Spotify")
        return

    logger.info(f"Playing '{main_playlist['name']}'")
    start_shuffled_playback(sp, main_playlist["uri"])


if __name__ == "__main__":
    main()
