import subprocess
import time
import os

def spotify_running_checker(sp):
    print("Checking for active Spotify devices ⏳")
    
    # Initialize our device
    devices = sp.devices()
    
    # Listing out our active devices
    active_devices = [d for d in devices['devices'] if d['is_active']]
    
    if active_devices:
        print ("Active Device Found ✅")
        return True
    
    # If we didnt find a device -> We got a problem
    print ("No Active Device(s) Found ⚠️")
    
    # Launch spotify.exe
    print ("Opening Spotify ⏳")
    
    # Open the file path for spotifys executable and start the file
    try:
        os.startfile(r"C:\Users\Blest\AppData\Roaming\Spotify\Spotify.exe")
        print ("Spotify Launched ✅")
    
    except Exception as e:
        print (f"Failed To Open {e} ❌")
        return False
    
    print ("Waiting For Spotify ⏳")
    time.sleep(3) # Wait for about 3 seconds for the app to launch itself
    
    # When launched -> Try to activate the device by starting playback
    devices = sp.devices()
    
    if devices['devices']:
        # Use the first available device
        target_device = devices['devices'][0]
        
        print (f"Starting Device: {target_device['name']} ⏳")
        
        try:
            # Start some playback to the device
            sp.start_playback(device_id = target_device['id'])
            time.sleep(0.3)
            
            #! IMMEDIATELY pause the playback -> We just need spotify to be active
            sp.pause_playback()
            
            print ("Device Activated ✅")
            return True
        
        except Exception as e:
            print (f"Couldn't Activate Device: {e} ❌")
            
        # If all else fails, tell user to play something manually and run script one more time
        print ("Please Play Something In Spotify Manually 👉 Run Script Again")
        return False