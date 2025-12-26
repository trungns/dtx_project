# PowerShell script to upgrade Odoo module on Windows
# Usage: .\upgrade-module.ps1 dtx_serial_ext

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$ModuleName
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Upgrading Odoo Module: $ModuleName" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
$dockerRunning = docker info 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}

# Check if containers are running
Write-Host "[1/3] Checking containers..." -ForegroundColor Green
$containers = docker-compose ps --services --filter "status=running" 2>$null
if ($containers -notcontains "web") {
    Write-Host "ERROR: Odoo container is not running!" -ForegroundColor Red
    Write-Host "Please run: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

# Upgrade module
Write-Host "[2/3] Upgrading module: $ModuleName..." -ForegroundColor Green
docker-compose exec web odoo -d dtx_dev -u $ModuleName --stop-after-init

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Module upgrade failed!" -ForegroundColor Red
    Write-Host "Check the error message above." -ForegroundColor Yellow
    exit 1
}

# Restart Odoo
Write-Host "[3/3] Restarting Odoo..." -ForegroundColor Green
docker-compose restart web | Out-Null

# Wait for Odoo to start
Write-Host ""
Write-Host "Waiting for Odoo to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Module upgraded successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access Odoo at: http://localhost:8069" -ForegroundColor Cyan
Write-Host ""
