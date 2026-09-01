$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== MARVIN INSTALLER ==="
Write-Host ""

& ".\build_marvin.ps1"

if ($LASTEXITCODE -ne 0) {
    throw "Falha no build do MARVIN."
}

$candidatos = @(
    "$env:ProgramFiles\Inno Setup 7\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 7\ISCC.exe",
    "$env:LOCALAPPDATA\Programs\Inno Setup 7\ISCC.exe",

    "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
)

$iscc = $candidatos |
    Where-Object {
        $_ -and (Test-Path $_)
    } |
    Select-Object -First 1

if (-not $iscc) {
    $cmd = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue

    if ($cmd) {
        $iscc = $cmd.Source
    }
}

if (-not $iscc) {
    throw "Inno Setup nao encontrado."
}

Remove-Item ".\release" `
    -Recurse `
    -Force `
    -ErrorAction SilentlyContinue

& $iscc ".\installer\MARVIN.iss"

if ($LASTEXITCODE -ne 0) {
    throw "Falha ao gerar o instalador."
}

Write-Host ""
Write-Host "================================="
Write-Host " INSTALADOR GERADO COM SUCESSO"
Write-Host "================================="
Write-Host ""
Write-Host ".\release\MARVIN-Setup.exe"
Write-Host ""
