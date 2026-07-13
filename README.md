# SpotifyPlaylistAutomator
Tool that automatically starts shuffling your primary Spotify playlist.

# Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Create an app at https://developer.spotify.com/dashboard to get a client ID and secret
3. Copy `.env.example` to `.env` and fill in `SPOTIFY_CLIENT_ID` / `SPOTIFY_CLIENT_SECRET`
4. Update the Spotify.exe path in `open_spotify.py` if your setup differs
5. Copy `spotify_auto_start.example.ahk` to `spotify_auto_start.ahk`, fill in your own paths, then run it with AutoHotkey. This filename is gitignored, so your personal copy with your paths in it never gets committed. Use pythonw.exe's full file path rather than just "pythonw" (see the comments in the example file for how to find it), and note it launches via a raw CreateProcess call rather than plain `Run`, since Windows 11's default-terminal-app setting can otherwise still flash a window and even kill the script if you close it.

# How To Use:
- The hotkey launches/wakes Spotify and plays your main playlist on shuffle, no terminal window shown
- If your main playlist is already playing, the same hotkey toggles play/pause instead of restarting it
- If Spotify is mid-update when triggered, it waits for that to finish before proceeding rather than failing
- If planning on shuffling from your PC Spotify app, make sure no other instances of Spotify on your account are running -> the program opens the PC client by default
- If you want to shuffle Spotify on another device, simply have that respective Spotify app open
- Logs go to `playlist_automator.log` next to the scripts, since the console window is hidden
