; ======================================================================
; spotify_auto_start.example.ahk
;
; Template hotkey script. This is NOT wired to a real path, copy it,
; rename it to spotify_auto_start.ahk (that filename is gitignored so
; your personal copy never gets committed), and fill in the two paths
; below for your own machine.
;
; Hotkey shown here: CTRL + ALT + SHIFT + M, change it to whatever you
; like, see the AutoHotkey docs for hotkey syntax.
; ======================================================================

^!+m::  ; CTRL + ALT + SHIFT + M
{
    ; First value is the command to run, including the full path to
    ; playlist_automator.py. pythonw.exe (not python.exe) so no
    ; console window ever flashes on screen.
    ;
    ; Second value is the working directory, should be the folder
    ; this project lives in, so playlist_automator.py can find its
    ; .env and write its log file next to itself.
    ;
    ; ", Hide" is a belt-and-suspenders backup in case pythonw still
    ; tries to show something.
    Run, pythonw "C:\path\to\PlaylistPlayer\playlist_automator.py", C:\path\to\PlaylistPlayer, Hide
    return
}
