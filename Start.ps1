param([int]$Port = 8765)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$DecisionLensPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $DecisionLensPython)) {
    $DecisionLensPrepared = Join-Path $PSScriptRoot '../../work/.venv/Scripts/python.exe'
    if (Test-Path -LiteralPath $DecisionLensPrepared) { $DecisionLensPython = (Resolve-Path -LiteralPath $DecisionLensPrepared).Path }
    else { throw 'Run Setup.ps1 once first.' }
}
$env:HF_HOME = Join-Path $PSScriptRoot '.cache/huggingface'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:HF_HUB_DISABLE_TELEMETRY = '1'
$env:DO_NOT_TRACK = '1'
Write-Host "Open http://127.0.0.1:$Port in your browser. Press Ctrl+C here to stop."
& $DecisionLensPython -m uvicorn decisionlens.server:app --host 127.0.0.1 --port $Port --no-access-log
