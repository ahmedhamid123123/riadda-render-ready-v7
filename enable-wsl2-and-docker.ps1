<#
enable-wsl2-and-docker.ps1

Usage: Run this script from an elevated PowerShell (Run as Administrator).
What it does:
- Enables required Windows features for WSL2/virtualization
- Installs the WSL kernel update (if needed)
- Sets WSL default version to 2
- Installs Ubuntu (via winget) if winget is available
- Installs Docker Desktop (via winget) if winget is available

This script attempts to be idempotent. You may be prompted to reboot.
#>

function Ensure-Admin {
    $current = [Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not $current.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Error "This script must be run as Administrator. Right-click PowerShell and choose 'Run as Administrator'."
        exit 1
    }
}

Ensure-Admin

Write-Host "Enabling Windows features: VirtualMachinePlatform and Microsoft-Windows-Subsystem-Linux..." -ForegroundColor Cyan
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

Write-Host "Installing/updating WSL kernel (if required)..." -ForegroundColor Cyan
$wslMsi = "$env:TEMP\wsl_update_x64.msi"
try {
    Invoke-WebRequest -Uri 'https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi' -OutFile $wslMsi -UseBasicParsing -ErrorAction Stop
    Start-Process msiexec.exe -ArgumentList '/i', $wslMsi, '/quiet', '/norestart' -Wait
    Write-Host "WSL kernel installer run (if it was needed)." -ForegroundColor Green
} catch {
    Write-Warning ("Could not download or run WSL kernel installer: {0}. You can install it manually from https://aka.ms/wsl2kernel" -f $_)
}

Write-Host "Setting default WSL version to 2..." -ForegroundColor Cyan
try {
    wsl --set-default-version 2
} catch {
    Write-Warning ("'wsl --set-default-version 2' failed or WSL is not available yet: {0}" -f $_)
}

function Install-With-Winget($id, $displayName) {
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "Installing $displayName via winget..." -ForegroundColor Cyan
        try {
            winget install --id $id -e --accept-package-agreements --accept-source-agreements
            Write-Host "$displayName install attempted." -ForegroundColor Green
        } catch {
            Write-Warning ("winget failed to install {0}: {1}" -f $displayName, $_)
        }
    } else {
        Write-Host "winget not available; skipping $displayName installation. Install it from Microsoft Store or download manually." -ForegroundColor Yellow
    }
}

Write-Host "Attempting to install an Ubuntu distribution (optional)..." -ForegroundColor Cyan
Install-With-Winget 'Canonical.Ubuntu' 'Ubuntu'

Write-Host "Attempting to install Docker Desktop (recommended) via winget..." -ForegroundColor Cyan
Install-With-Winget 'Docker.DockerDesktop' 'Docker Desktop'

Write-Host "
Done. Notes:
- If Docker Desktop was installed, open it and follow the initial setup (enable WSL2 integration if prompted).
- You may need to reboot to apply Virtualization/WSL changes.
" -ForegroundColor Green

Write-Host "If a reboot is required, run: Restart-Computer" -ForegroundColor Yellow

exit 0
