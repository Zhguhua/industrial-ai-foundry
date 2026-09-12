$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example"
}

Write-Host "Starting Industrial AI Foundry..."
docker compose up --build -d

Write-Host "Waiting for API and demo seed..."
$max = 60
for ($i = 0; $i -lt $max; $i++) {
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 2
        if ($health.status -eq "ok") { break }
    } catch {}
    Start-Sleep -Seconds 2
}

docker compose wait demo-seed

Write-Host ""
Write-Host "Industrial AI Foundry is ready."
Write-Host "UI:       http://localhost:5173"
Write-Host "API:      http://localhost:8000/docs"
Write-Host "Neo4j:    http://localhost:7474"
Write-Host "MinIO:    http://localhost:9001"
Write-Host ""
Write-Host "Run smoke test: python scripts/smoke-test.py"
