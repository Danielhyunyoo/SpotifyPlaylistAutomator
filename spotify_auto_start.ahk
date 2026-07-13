; ======================================================================
; spotify_auto_start.ahk
;
; Hotkey: CTRL + ALT + SHIFT + M
; Runs playlist_automator.py to launch/wake Spotify and play the main
; playlist on shuffle, or toggle play/pause if it's already playing.
;
; Uses pythonw.exe (not python.exe) so no console window ever flashes
; on screen, and ", Hide" as a belt-and-suspenders backup.
; ======================================================================

^!+m::  ; CTRL + ALT + SHIFT + M
{
    Run, pythonw "C:\Users\Blest\Documents\VScode - Python\PlaylistPlayer\playlist_automator.py", C:\Users\Blest\Documents\VScode - Python\PlaylistPlayer, Hide
    return
}
