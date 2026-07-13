# SpotifyPlaylistAutomator
Tool that automatically starts shuffling your primary Spotify playlist.

# Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Create an app at https://developer.spotify.com/dashboard to get a client ID and secret
3. Copy `.env.example` to `.env` and fill in `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET`
4. Update the Spotify.exe path in `open_spotify.py` and the script path in `spotify_auto_start.ahk` if your setup differs
5. Run `spotify_auto_start.ahk` with AutoHotkey

# How To Use:
- The keyboard shortcut "CTRL + ALT + SHIFT + M" launches/wakes Spotify and plays your main playlist on shuffle, no terminal window shown
- If your main playlist is already playing, the same shortcut toggles play/pause instead of restarting it
- If planning on shuffling from your PC Spotify app, make sure no other instances of Spotify on your account are running -> the program opens the PC client by default
- If you want to shuffle Spotify on another device, simply have that respective Spotify app open
- Logs go to `playlist_automator.log` next to the scripts, since the console window is hidden
