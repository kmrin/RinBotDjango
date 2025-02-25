if ($PSVersionTable.PSVersion.Major -lt 7) {
    Write-Error "This script requires PowerShell 7 or later. Please install it from https://github.com/PowerShell/PowerShell"
    exit 1
}

try {
    Import-Module powershell-yaml -ErrorAction Stop
} catch {
    Write-Error "The powershell-yaml module is required. Please install it with: Install-Module -Name powershell-yaml -Scope CurrentUser"
    exit 1
}

Write-Host "Initializing environment variables from configuration..." -ForegroundColor Cyan
try {
    . "$PSScriptRoot\rinbot\scripts\init_postgres_env.ps1"
} catch {
    Write-Error "Failed to initialize environment variables: $_"
    exit 1
}

try {
    docker info | Out-Null
} catch {
    Write-Error "Docker is not running. Please start Docker Desktop and try again."
    exit 1
}

$networkExists = docker network ls --format "{{.Name}}" | Where-Object { $_ -eq "RinNetwork" }
if (-not $networkExists) {
    Write-Host "Creating RinNetwork Docker network..." -ForegroundColor Yellow
    docker network create RinNetwork
}

Write-Host "Starting Docker Compose services..." -ForegroundColor Green
docker-compose up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nServices started successfully!" -ForegroundColor Green
    Write-Host "`nTo create a superuser, run:" -ForegroundColor Yellow
    Write-Host "docker exec -it rinbot-django python scripts/create_superuser.py" -ForegroundColor DarkYellow
} else {
    Write-Host "`nFailed to start services. Check the error messages above." -ForegroundColor Red
}
