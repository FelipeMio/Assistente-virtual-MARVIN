$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== MARVIN BUILD ==="
Write-Host ""

Stop-Process `
    -Name MARVIN `
    -Force `
    -ErrorAction SilentlyContinue

Start-Sleep -Seconds 1

Remove-Item `
    ".\build" `
    -Recurse `
    -Force `
    -ErrorAction SilentlyContinue

Remove-Item `
    ".\dist" `
    -Recurse `
    -Force `
    -ErrorAction SilentlyContinue

python -m PyInstaller `
    --clean `
    --noconfirm `
    ".\MARVIN.spec"

if ($LASTEXITCODE -ne 0) {
    throw "Falha ao gerar o MARVIN."
}

Write-Host ""
Write-Host "Build concluido."
Write-Host ""
Write-Host "Executavel:"
Write-Host ".\dist\MARVIN\MARVIN.exe"
Write-Host ""
