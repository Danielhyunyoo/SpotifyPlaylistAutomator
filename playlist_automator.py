import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth

# Import OpenSpotify.py
from open_spotify import spotify_running_checker

#! Credentials
client_id = "8ce13e340558405597c4be0507dcf7b4"
client_secret = "318c5b5787c94466aac72fd730df6dc5"
redirect_uri = "http://127.0.0.1:8000/callback"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = client_id, client_secret = client_secret, redirect_uri = redirect_uri, scope = "user-read-playback-state user-modify-playback-state playlist-read-private"))

#======================================================================================================================================#

#! Automatically Open Spotify If Necessary
if not spotify_running_checker(sp):
    print ("Failed To Open Spotify ⚠️")
    
    exit()

#! Finding Main Playlist
playlists = sp.current_user_playlists(limit = 50) # 50 limit to ensure we grab ALL our playlists

# Designate the main playlist
main_playlist = None

# Loop through all our playlists -> If we find the main playlist -> Designate it
for playlist in playlists['items']:
    if playlist['name'] == "It's Raining After All":
        main_playlist = playlist
        
        break

# If we found our main playlist -> Start running it
if main_playlist:
    print (f"Playing '{main_playlist['name']}' ⏳")
    
    time.sleep(2)
    
    try:
        sp.start_playback(context_uri = main_playlist['uri'])
        
        time.sleep(1)
        
        sp.shuffle(True)
        
        print ("Playlist Is Running ✅")
    
    except Exception as e:
        print (f"Error: {e}")
        print ("Attempt Running Script Again ⚠️")
    
else:
    # If we can't find playlist -> Tell user
    print ("Couldn't Find Main Playlist ⚠️")
