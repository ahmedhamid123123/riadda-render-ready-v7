<#
scripts/migrate_to_postgres.ps1

PowerShell helper to migrate Django project from SQLite to PostgreSQL on Windows.

Usage (PowerShell):
  1) Edit or supply values when prompted.
  2) Ensure `psql` is available in PATH (Postgres client).
  3) Run: `.	emplates\scripts\migrate_to_postgres.ps1` or `.unctions\scripts\migrate_to_postgres.ps1`

This script will:
 - prompt for DB name, app user and password
 - run create_riadda_db.sql via psql
 - ensure python deps are installed
 - create a UTF-8 data dump (if not present)
 - run Django migrations against Postgres
 - load fixture `data.json` into Postgres

Note: Run this script on the machine where Postgres is reachable and `psql` can connect as a superuser.
#>

param(
    [string]$DbName = "riadda",
    [string]$AppUser = "riadda_app",
    [string]$AppPass = "",
    [string]$PostgresSuperUser = "postgres",
    [string]$PgHost = "127.0.0.1",
    [int]$PgPort = 5432
)

function Read-Secret($prompt){
    if ($AppPass) { return $AppPass }
    Write-Host $prompt -NoNewline
    $sec = Read-Host -AsSecureString
    return [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
}

if (-not (Get-Command psql -ErrorAction SilentlyContinue)){
    Write-Error "psql not found in PATH. Install PostgreSQL client or add psql to PATH and re-run."
    exit 1
}

if (-not $AppPass){
    $AppPass = Read-Secret "Enter DB app user password: "
}

$sqlTemplate = Join-Path $PSScriptRoot "create_riadda_db.sql"
if (-not (Test-Path $sqlTemplate)){
    Write-Error "SQL template $sqlTemplate not found."
    exit 1
}

Write-Host "Creating database and role (you may be prompted for postgres password)..."
& psql -U $PostgresSuperUser -h $PgHost -p $PgPort -v db_name=$DbName -v app_user=$AppUser -v app_pass="$AppPass" -f $sqlTemplate
if ($LASTEXITCODE -ne 0){ Write-Error "psql command failed"; exit 1 }

Write-Host "Installing Python dependencies..."
pip install -r requirements.txt

if (-not (Test-Path data.json)){
    Write-Host "Creating UTF-8 fixture dump (data.json)..."
    $env:PYTHONIOENCODING = "utf-8"
    python -X utf8 manage.py dumpdata --natural-primary --natural-foreign --exclude auth.permission --exclude contenttypes --exclude sessions | Out-File -Encoding utf8 data.json
}

Write-Host "Set environment variables or create .env file now (press Enter to continue)..."
Read-Host

Write-Host "Running migrations against Postgres..."
python manage.py migrate
if ($LASTEXITCODE -ne 0){ Write-Error "migrate failed"; exit 1 }

Write-Host "Loading fixture data.json into Postgres (may take time)..."
python manage.py loaddata data.json
if ($LASTEXITCODE -ne 0){ Write-Error "loaddata failed"; exit 1 }

Write-Host "Migration complete. Verify the app by running: python manage.py runserver"
