param(
    [string]$TaskName = "TNT-AzureTokenRefresh",
    [string]$ResourceGroup = "TNT-RG",
    [string]$WebAppName = "tnt-bc5-chatbot-api",
    [int]$LogCheckSeconds = 45
)

$ErrorActionPreference = "Stop"

$scriptPath = Join-Path $PSScriptRoot "auto_refresh_remote_token.ps1"
if (-not (Test-Path $scriptPath)) {
    throw "Missing script: $scriptPath"
}

$args = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", "`"$scriptPath`"",
    "-ResourceGroup", "`"$ResourceGroup`"",
    "-WebAppName", "`"$WebAppName`"",
    "-IntervalMinutes", "60",
    "-Once",
    "-CheckLogStream",
    "-LogCheckSeconds", "$LogCheckSeconds"
) -join " "

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $args
$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Hours 1) `
    -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Auto-refresh Azure access token hourly and validate App Service logs." `
    -Force | Out-Null

$info = Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo

Write-Host "Scheduled task installed." -ForegroundColor Green
Write-Host "Task Name: $TaskName" -ForegroundColor Green
Write-Host "Runs every: 1 hour" -ForegroundColor Green
Write-Host "Next Run Time: $($info.NextRunTime)" -ForegroundColor Green
Write-Host "Log check: enabled ($LogCheckSeconds sec)" -ForegroundColor Green
Write-Host "PowerShell Args: $args" -ForegroundColor Green
