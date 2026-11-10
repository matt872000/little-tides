$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $projectPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
    if (-not (Test-Path -LiteralPath $projectPython)) {
        throw 'Create .venv and install requirements first; see README.md.'
    }
    & $projectPython -m PyInstaller --noconfirm --windowed --onedir --exclude-module numpy --exclude-module pygame.examples --exclude-module pygame.tests --name 'Little Tides' main.py
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed.' }
    $gameDirectory = Join-Path $PSScriptRoot 'dist/Little Tides'
    Copy-Item -LiteralPath 'licenses' -Destination $gameDirectory -Recurse -Force
    Copy-Item -LiteralPath 'THIRD-PARTY.txt','README.md' -Destination $gameDirectory -Force
    Write-Output ('Game built at: ' + (Join-Path $gameDirectory 'Little Tides.exe'))
} finally {
    Pop-Location
}
