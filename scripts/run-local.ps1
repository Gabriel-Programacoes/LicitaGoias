$ErrorActionPreference = 'Stop'

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$environmentFile = Join-Path $projectRoot '.env'
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $environmentFile)) {
    throw 'Arquivo .env ausente. Consulte docs/fase-2-operacao.md.'
}
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Ambiente .venv ausente. Instale as dependencias do projeto.'
}

foreach ($line in Get-Content -LiteralPath $environmentFile) {
    if ($line -match '^\s*([A-Z][A-Z0-9_]*)=(.*)$') {
        [Environment]::SetEnvironmentVariable($Matches[1], $Matches[2], 'Process')
    }
}

Push-Location $projectRoot
try {
    & $python -m uvicorn licitagoias.api.app:app --reload --host 127.0.0.1 --port 8000
    if ($LASTEXITCODE -ne 0) {
        throw "A API encerrou com codigo $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
