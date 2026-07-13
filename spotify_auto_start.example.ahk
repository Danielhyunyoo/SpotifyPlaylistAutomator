; ======================================================================
; spotify_auto_start.example.ahk
;
; Template hotkey script. This is NOT wired to a real path, copy it,
; rename it to spotify_auto_start.ahk (that filename is gitignored so
; your personal copy never gets committed), and fill in the paths in
; the hotkey block below for your own machine.
;
; Hotkey shown here: CTRL + ALT + SHIFT + M, change it to whatever you
; like, see the AutoHotkey docs for hotkey syntax.
;
; This launches pythonw.exe through the raw Windows CreateProcess API
; with CREATE_NO_WINDOW instead of AHK's built-in Run ..., Hide.
; Run ..., Hide can still show a window on Windows 11 if "Windows
; Terminal" is set as the default terminal app, it overrides simple
; show/hide hints, and closing that window can kill the script
; mid-run. CREATE_NO_WINDOW is a real process-creation flag Windows
; always honors, so this sidesteps the problem entirely.
;
; Find your pythonw.exe's full path with this in PowerShell:
;   $py = (Get-Command python).Source
;   Get-ChildItem (Split-Path $py) -Filter "pythonw.exe"
; ======================================================================

^!+m::  ; CTRL + ALT + SHIFT + M
{
    RunHidden("C:\path\to\Python\pythonw.exe", "C:\path\to\PlaylistPlayer\playlist_automator.py", "C:\path\to\PlaylistPlayer")
    return
}

; ----------------------------------------------------------------------
; RunHidden(exePath, scriptPath, workDir)
;
; Launches exePath with scriptPath as its single argument, completely
; invisibly, via CreateProcess + CREATE_NO_WINDOW. See the comment
; block above for why this exists instead of a plain Run ..., Hide.
; ----------------------------------------------------------------------
RunHidden(exePath, scriptPath, workDir)
{
    cmdLine := """" . exePath . """ """ . scriptPath . """"

    ; STARTUPINFO's real size differs between 32-bit and 64-bit builds
    ; of AutoHotkey (it's full of pointer-sized fields), has to match
    ; exactly or CreateProcess won't accept it.
    cbSize := (A_PtrSize = 8) ? 104 : 68
    VarSetCapacity(si, cbSize, 0)
    NumPut(cbSize, si, 0, "UInt")

    ; PROCESS_INFORMATION, over-allocated a bit for simplicity, only
    ; the first two pointer-sized fields (hProcess, hThread) get used
    VarSetCapacity(pi, 32, 0)

    CREATE_NO_WINDOW := 0x08000000

    success := DllCall("CreateProcess"
        , "Str", exePath
        , "Str", cmdLine
        , "Ptr", 0
        , "Ptr", 0
        , "Int", 0
        , "UInt", CREATE_NO_WINDOW
        , "Ptr", 0
        , "Str", workDir
        , "Ptr", &si
        , "Ptr", &pi)

    if (success)
    {
        DllCall("CloseHandle", "Ptr", NumGet(pi, 0, "Ptr"))
        DllCall("CloseHandle", "Ptr", NumGet(pi, A_PtrSize, "Ptr"))
    }

    return success
}
