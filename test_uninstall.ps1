# Exercise only bounded uninstall helpers on disposable workspace data.
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath($PSScriptRoot)
$fixture=Join-Path $workspace ('.uninstall-test-'+[Guid]::NewGuid().ToString('N'))
if (-not [IO.Path]::GetFullPath($fixture).StartsWith($workspace+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Invalid test fixture path' }
New-Item -ItemType Directory -Path $fixture | Out-Null
$installRoot=$fixture
try {
 $tokens=$null;$errors=$null
 $tree=[Management.Automation.Language.Parser]::ParseFile((Join-Path $workspace 'uninstall.ps1'),[ref]$tokens,[ref]$errors)
 if ($errors) { throw 'Uninstaller syntax errors' }
 foreach ($function in $tree.FindAll({param($node) $node -is [Management.Automation.Language.FunctionDefinitionAst]},$true)) {
  if ($function.Name -in @('CheckedPath','CheckTree','RemoveTree')) { . ([scriptblock]::Create($function.Extent.Text)) }
 }
 $rejected=$false
 try { CheckedPath '..\outside.txt' | Out-Null } catch { $rejected=$true }
 if (-not $rejected) { throw 'Traversal was accepted' }
 $managed=CheckedPath '.venv'
 New-Item -ItemType Directory -Path $managed | Out-Null
 Set-Content -LiteralPath (Join-Path $managed 'test-only.txt') -Value 'synthetic'
 Set-Content -LiteralPath (Join-Path $fixture 'personal.txt') -Value 'keep'
 CheckTree $managed
 RemoveTree $managed
 if (Test-Path -LiteralPath $managed) { throw 'Managed directory not removed' }
 if (-not (Test-Path -LiteralPath (Join-Path $fixture 'personal.txt'))) { throw 'Unmanaged file removed' }
 'PASS: uninstall path traversal rejected, owned tree removed, unmanaged file preserved'
} finally {
 # Known, newly created fixture only; no recursive deletion against a derived user directory.
 Remove-Item -LiteralPath (Join-Path $fixture 'personal.txt') -Force -ErrorAction SilentlyContinue
 if (-not (Get-ChildItem -LiteralPath $fixture -Force)) { Remove-Item -LiteralPath $fixture -Force }
}
