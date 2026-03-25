Set oFSO = CreateObject("Scripting.FileSystemObject")
Set oShell = CreateObject("WScript.Shell")

sDir = oFSO.GetParentFolderName(WScript.ScriptFullName)
sBat = sDir & "\start.bat"

If Not oFSO.FileExists(sBat) Then
    MsgBox "start.bat not found in:" & vbCrLf & sDir, vbCritical, "CatPrice"
    WScript.Quit
End If

' windowStyle 0 = hidden (no terminal flicker)
oShell.Run Chr(34) & sBat & Chr(34), 0, False
