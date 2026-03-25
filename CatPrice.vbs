Set oFSO = CreateObject("Scripting.FileSystemObject")
Set oShell = CreateObject("WScript.Shell")

sDir = oFSO.GetParentFolderName(WScript.ScriptFullName)
sExe = sDir & "\dist-electron\win-unpacked\CatPrice.exe"
sBat = sDir & "\start.bat"

If oFSO.FileExists(sExe) Then
    oShell.Run Chr(34) & sExe & Chr(34), 1, False
    WScript.Quit
End If

If Not oFSO.FileExists(sBat) Then
    MsgBox "CatPrice.exe or start.bat not found in:" & vbCrLf & sDir, vbCritical, "CatPrice"
    WScript.Quit
End If

' Fallback to batch launcher when the packaged app is unavailable.
oShell.Run Chr(34) & sBat & Chr(34), 1, False
