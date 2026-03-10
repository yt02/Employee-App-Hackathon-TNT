param(
    [string]$TaskName = "TNT-AzureTokenRefresh"
)

$ErrorActionPreference = "Stop"

Write-Host "Removing scheduled task '$TaskName'..." -ForegroundColor Cyan
schtasks /Delete /TN $TaskName /F | Out-Null
Write-Host "Scheduled task removed." -ForegroundColor Green

