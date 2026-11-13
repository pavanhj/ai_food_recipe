# AI Food Recipe System Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Starting AI Food Recipe System..." -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

$CurrentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $CurrentDir

$PyExe = "python"
if (Test-Path ".\.venv\Scripts\python.exe") {
    $PyExe = ".\.venv\Scripts\python.exe"
}

Start-Process "http://127.0.0.1:5000"
& $PyExe app.py
