param([switch]$WithGenerator, [switch]$Dev)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe')) {
    py -3.11 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.11 from python.org with the Windows py launcher, then run Setup.ps1 again.' }
}
$DecisionLensPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
$DecisionLensRequirements = 'requirements-lock.txt' # Tested Windows/Python 3.11 environment; includes verification tools.
& $DecisionLensPython -m pip install -r $DecisionLensRequirements
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
if ($WithGenerator) { & $DecisionLensPython scripts/prepare_models.py --generation }
else { & $DecisionLensPython scripts/prepare_models.py }
if ($LASTEXITCODE -ne 0) { throw 'Model download failed. Keyword search still works; retry setup later for semantic search.' }
Write-Host 'Setup complete. Launch with: powershell -ExecutionPolicy Bypass -File .\Start.ps1'
