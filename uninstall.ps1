# Per-user SARU uninstaller. No administrator privileges or AppData deletion.
param([switch]$ValidateOnly)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
$installRoot = [IO.Path]::GetFullPath($PSScriptRoot).TrimEnd('\')
$registryPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\SARU_AI_Studio'
function CheckedPath([string]$relative) {
 if ([IO.Path]::IsPathRooted($relative) -or $relative.Contains(':') -or ($relative -split '[\\/]') -contains '..') { throw 'Unsafe managed path.' }
 $candidate = [IO.Path]::GetFullPath((Join-Path $installRoot $relative))
 if (-not $candidate.StartsWith($installRoot + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Path outside SARU install folder.' }
 $probe = $candidate
 while ($probe -ne $installRoot) {
  if (Test-Path -LiteralPath $probe) {
   if ((Get-Item -LiteralPath $probe -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked folders are not removed. Remove the link manually first.' }
  }
  $probe = [IO.Path]::GetDirectoryName($probe)
 }
 return $candidate
}
function CheckTree([string]$path) {
 if (-not (Test-Path -LiteralPath $path)) { return }
 $item = Get-Item -LiteralPath $path -Force
 if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked file/folder detected; uninstall stopped.' }
 if ($item.PSIsContainer) {
  foreach ($child in Get-ChildItem -LiteralPath $path -Force) { CheckTree $child.FullName }
 }
}
function RemoveTree([string]$path) {
 if (-not (Test-Path -LiteralPath $path)) { return }
 $item = Get-Item -LiteralPath $path -Force
 if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked file/folder detected; uninstall stopped.' }
 if ($item.PSIsContainer) {
  foreach ($child in Get-ChildItem -LiteralPath $path -Force) { RemoveTree $child.FullName }
 }
 Remove-Item -LiteralPath $path -Force
}
try {
 $manifest = Get-Content -LiteralPath (Join-Path $installRoot 'saru-install.json') -Raw | ConvertFrom-Json
 if ($manifest.app_id -ne 'SARU_AI_Studio' -or [IO.Path]::GetFullPath($manifest.install_location).TrimEnd('\') -ne $installRoot) { throw 'Invalid installation manifest. Nothing removed.' }
 $registered = Get-ItemProperty -LiteralPath $registryPath -ErrorAction SilentlyContinue
 if ($registered -and [IO.Path]::GetFullPath($registered.InstallLocation).TrimEnd('\') -ne $installRoot) { throw 'A different SARU installation is registered. Nothing removed.' }
 $files = @($manifest.files | ForEach-Object { CheckedPath $_ })
 foreach ($name in $manifest.managed_directories) { if ($name -notin @('.venv','.advanced-env','.python-runtime','.saru-backups','__pycache__')) { throw 'Unknown managed directory.' } }
 $directories = @($manifest.managed_directories | ForEach-Object { CheckedPath $_ })
 foreach ($path in @($files) + @($directories)) { CheckTree $path }
 if ($ValidateOnly) { Write-Output 'Uninstall manifest and path validation passed. No changes made.'; exit 0 }
 $processes = Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^pythonw?\.exe$' -and $_.CommandLine -and $_.CommandLine.IndexOf((Join-Path $installRoot 'app.py'),[StringComparison]::OrdinalIgnoreCase) -ge 0 }
 if ($processes) { throw 'Close SARU and its floating assistant before uninstalling.' }
 $answer = [Windows.Forms.MessageBox]::Show("Uninstall SARU AI from:`n$installRoot`n`nSettings, memory and images in AppData will be kept. Unrecognized files will also be kept.", 'Uninstall SARU AI', 'YesNo', 'Question')
 if ($answer -ne 'Yes') { exit 0 }
 $shell = New-Object -ComObject WScript.Shell
 foreach ($special in @('Desktop','Startup','Programs')) {
  $shortcutPath = Join-Path $shell.SpecialFolders.Item($special) 'SARU AI.lnk'
  if (Test-Path -LiteralPath $shortcutPath) {
   $link = $shell.CreateShortcut($shortcutPath)
   if ($link.TargetPath -eq (Join-Path $installRoot 'Start SARU AI.cmd')) { Remove-Item -LiteralPath $shortcutPath -Force }
  }
 }
 # Preflight above checks every path before any removal; remove only managed content.
 foreach ($path in $directories) { RemoveTree $path }
 foreach ($path in $files) { if (Test-Path -LiteralPath $path -PathType Leaf) { Remove-Item -LiteralPath $path -Force } }
 # Remove empty guide subfolders only; user-created content is retained.
 $guide = CheckedPath 'MYRA_OFFICIAL_GUIDES'
 function RemoveEmpty([string]$path) {
  if (-not (Test-Path -LiteralPath $path -PathType Container)) { return }
  foreach ($child in Get-ChildItem -LiteralPath $path -Directory -Force) { RemoveEmpty $child.FullName }
  if (-not (Get-ChildItem -LiteralPath $path -Force | Select-Object -First 1)) { Remove-Item -LiteralPath $path -Force }
 }
 RemoveEmpty $guide
 if ($registered) { Remove-Item -LiteralPath $registryPath -Force }
 if (-not (Get-ChildItem -LiteralPath $installRoot -Force | Select-Object -First 1)) { Remove-Item -LiteralPath $installRoot -Force }
 [Windows.Forms.MessageBox]::Show('SARU AI was uninstalled. Your AppData settings and memory were kept.','SARU AI') | Out-Null
} catch {
 [Windows.Forms.MessageBox]::Show($_.Exception.Message,'SARU uninstall needs attention','OK','Error') | Out-Null
 exit 1
}
