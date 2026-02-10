if (Test-Path '.env') {
    Get-Content '.env' | ForEach-Object {
        if ($_ -and -not $_.TrimStart().StartsWith('#')) {
            $parts = $_ -split '=', 2
            if ($parts.Count -eq 2) {
                $name = $parts[0].Trim()
                $value = $parts[1].Trim().Trim('"')
                [System.Environment]::SetEnvironmentVariable($name, $value, 'Process')
            }
        }
    }
    Write-Host "Loaded .env into process environment." -ForegroundColor Green
} else {
    Write-Host ".env not found; no variables loaded." -ForegroundColor Yellow
}

Write-Host "Starting Django runserver (127.0.0.1:8000) -- use CTRL-C to stop." -ForegroundColor Cyan
python manage.py runserver 127.0.0.1:8000 --noreload
