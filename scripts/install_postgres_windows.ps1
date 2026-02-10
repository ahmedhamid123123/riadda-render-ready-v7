<#
Install PostgreSQL on Windows via Chocolatey and create the application DB/user.

Run this script as Administrator from the project root:
  PowerShell -ExecutionPolicy Bypass -File .\scripts\install_postgres_windows.ps1

What the script does:
- Installs Chocolatey if missing
- Installs PostgreSQL 15 via Chocolatey (silent) and sets a generated postgres password
- Reads `.env` to get `DJANGO_DB_NAME`, `DJANGO_DB_USER`, `DJANGO_DB_PASS` and creates that user/database

Notes:
- You must run as Administrator. The script prints the generated postgres superuser password.
- If you prefer the GUI installer, use the README instructions instead.
#>

function ExitWith($msg, $code=1) {
    Write-Error $msg
    exit $code
}

if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    ExitWith "This script must be run as Administrator. Open PowerShell as Administrator and re-run."
}

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$envFile = Join-Path $projectRoot ".env"
if (-not (Test-Path $envFile)) {
    ExitWith ".env file not found in project root ($projectRoot). Create it or run this script from the project root."
}

Write-Host "Reading .env..."
$envLines = Get-Content $envFile | Where-Object { $_ -and ($_ -notmatch '^[#;]') }
$envMap = @{}
foreach ($line in $envLines) {
    if ($line -match '^([^=]+)=(.*)$') {
        $k = $matches[1].Trim()
        $v = $matches[2].Trim(" `\"')
        $envMap[$k] = $v
    }
}

$dbName = $envMap['DJANGO_DB_NAME']  ? $envMap['DJANGO_DB_NAME']  : 'riadda'
$dbUser = $envMap['DJANGO_DB_USER']  ? $envMap['DJANGO_DB_USER']  : 'riadda_app'
$dbPass = $envMap['DJANGO_DB_PASS']  ? $envMap['DJANGO_DB_PASS']  : ''

if (-not $dbPass) {
    Write-Warning "DJANGO_DB_PASS not set in .env. The DB user will be created without password; you may edit it later."
}

function Ensure-Chocolatey {
    if (Get-Command choco -ErrorAction SilentlyContinue) { return }
    Write-Host "Installing Chocolatey (requires internet)..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
        ExitWith "Chocolatey install failed or is not available in PATH."
    }
}

Ensure-Chocolatey

# Generate a strong password for the postgres superuser for this installation
function New-RandomPassword($len=24) {
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $bytes = New-Object byte[] $len
    $rng.GetBytes($bytes)
    [Convert]::ToBase64String($bytes).Substring(0,$len)
}

$pgSuperPass = New-RandomPassword
Write-Host "Generated postgres superuser password will be used for installation (displaying briefly):"
Write-Host $pgSuperPass -ForegroundColor Yellow

Write-Host "Installing PostgreSQL 15 via Chocolatey..."
$chocoArgs = "install postgresql --version=15.4 --params '""/Password:$pgSuperPass""' -y"
choco $chocoArgs

Write-Host "Waiting for PostgreSQL service to appear..."
Start-Sleep -Seconds 4
for ($i=0;$i -lt 30;$i++) {
    $svc = Get-Service | Where-Object { $_.DisplayName -like '*PostgreSQL*' }
    if ($svc) { break }
    Start-Sleep -Seconds 2
}

if (-not $svc) { Write-Warning "PostgreSQL service not found — installation may have failed. Check Chocolatey output." }

# Locate psql
$psqlCmd = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psqlCmd) {
    # common install path
    $possible = "C:\Program Files\PostgreSQL\15\bin\psql.exe"
    if (Test-Path $possible) { $psqlCmd = $possible }
}
if (-not $psqlCmd) { ExitWith "psql not found. Ensure PostgreSQL installed and psql.exe is on PATH." }

Write-Host "Creating database and application user..."
$createUserSql = "DO \$\$ BEGIN IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$dbUser') THEN CREATE ROLE \"$dbUser\" WITH LOGIN PASSWORD '$dbPass'; END IF; END \$\$;";

# Use PGPASSWORD env to run psql commands non-interactively as postgres
$old = $env:PGPASSWORD
$env:PGPASSWORD = $pgSuperPass

# Create user
& $psqlCmd -U postgres -h 127.0.0.1 -c $createUserSql
# Create database owned by user (ignore errors if exists)
& $psqlCmd -U postgres -h 127.0.0.1 -c "CREATE DATABASE \"$dbName\" OWNER \"$dbUser\";" 2>$null
& $psqlCmd -U postgres -h 127.0.0.1 -c "GRANT ALL PRIVILEGES ON DATABASE \"$dbName\" TO \"$dbUser\";"

$env:PGPASSWORD = $old

Write-Host "PostgreSQL installation and DB/user creation complete."
Write-Host "Postgres superuser password (keep it safe):" -ForegroundColor Cyan
Write-Host $pgSuperPass -ForegroundColor Yellow

Write-Host "Update your .env if needed and then run (in your venv):"
Write-Host "  python -m pip install -r requirements.txt" -ForegroundColor Green
Write-Host "  python manage.py migrate" -ForegroundColor Green
Write-Host "  python manage.py runserver" -ForegroundColor Green
