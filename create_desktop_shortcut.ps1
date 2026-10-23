param([string]$PythonW)
$ErrorActionPreference='Stop'
$sourceRoot=[IO.Path]::GetFullPath($PSScriptRoot)
if (-not (Test-Path -LiteralPath (Join-Path $sourceRoot 'launch_saru.py'))) { throw 'SARU launcher missing' }
if (-not (Test-Path -LiteralPath $PythonW)) { throw 'Python launcher missing' }
$shell=New-Object -ComObject WScript.Shell
$desktop=$shell.SpecialFolders.Item('Desktop')
$linkPath=Join-Path $desktop 'SARU AI.lnk'
$link=$shell.CreateShortcut($linkPath)
$link.TargetPath=$PythonW
$link.Arguments='"'+(Join-Path $sourceRoot 'launch_saru.py')+'"'
$link.WorkingDirectory=$sourceRoot
$link.IconLocation=(Join-Path $sourceRoot 'saru.ico')+',0'
$link.Description='SARU AI desktop assistant'
$link.Save()
$verified=$shell.CreateShortcut($linkPath)
if ($verified.TargetPath -ne $PythonW -or $verified.Arguments -notlike '*launch_saru.py*') { throw 'Shortcut verification failed' }
Write-Output ('Verified desktop shortcut: '+$linkPath)
