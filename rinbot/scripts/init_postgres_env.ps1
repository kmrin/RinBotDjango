Import-Module powershell-yaml -ErrorAction Stop

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ConfigFile = Join-Path -Path (Split-Path -Parent $ScriptDir) -ChildPath "lavalink\config\rinbot.yml"

if (-not (Test-Path $ConfigFile)) {
    Write-Error "Configuration file not found: $ConfigFile"
    exit 1
}

Write-Host "Loading database configuration from rinbot.yml..."
$Config = Get-Content -Path $ConfigFile -Raw | ConvertFrom-Yaml

$env:DB_NAME = $Config.database.name
$env:DB_USER = $Config.database.user
$env:DB_PASSWORD = $Config.database.password
$env:DB_HOST = $Config.database.host
$env:DB_PORT = $Config.database.port

$env:POSTGRES_DB = $env:DB_NAME
$env:POSTGRES_USER = $env:DB_USER
$env:POSTGRES_PASSWORD = $env:DB_PASSWORD
