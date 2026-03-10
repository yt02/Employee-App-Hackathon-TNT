# Auto-refresh AZURE_ACCESS_TOKEN and push it to Azure App Service on a schedule.
# Use this only when you cannot use Managed Identity yet.
#
# Example:
#   powershell -ExecutionPolicy Bypass -File .\auto_refresh_remote_token.ps1
#   powershell -ExecutionPolicy Bypass -File .\auto_refresh_remote_token.ps1 -IntervalMinutes 60 -Once -CheckLogStream

param(
    [string]$ResourceGroup = "TNT-RG",
    [string]$WebAppName = "tnt-bc5-chatbot-api",
    [int]$IntervalMinutes = 60,
    [switch]$Once,
    [switch]$UpdateLocalEnv,
    [switch]$CheckLogStream,
    [int]$LogCheckSeconds = 45,
    [int]$LogCheckTailLines = 120
)

$ErrorActionPreference = "Stop"

function Update-LocalEnvToken {
    param([string]$TokenValue)

    $envPath = Join-Path $PSScriptRoot ".env"
    if (-not (Test-Path $envPath)) {
        return
    }

    $content = Get-Content $envPath
    $updated = $false
    $newContent = $content | ForEach-Object {
        if ($_ -match "^AZURE_ACCESS_TOKEN=") {
            $updated = $true
            "AZURE_ACCESS_TOKEN=$TokenValue"
        } else {
            $_
        }
    }

    if (-not $updated) {
        $newContent += "AZURE_ACCESS_TOKEN=$TokenValue"
    }

    $newContent | Set-Content $envPath
}

function Test-RemoteLogStream {
    param(
        [int]$DurationSeconds = 45,
        [int]$TailLines = 120
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] Checking App Service log stream for $DurationSeconds second(s)..." -ForegroundColor Cyan

    # Ensure application logging is enabled so log tail can return entries.
    az webapp log config `
        --resource-group $ResourceGroup `
        --name $WebAppName `
        --application-logging filesystem `
        --level information | Out-Null

    $logFile = Join-Path $env:TEMP ("$WebAppName-logtail-{0}.log" -f [Guid]::NewGuid().ToString("N"))
    $tailCommand = "az webapp log tail --resource-group `"$ResourceGroup`" --name `"$WebAppName`""

    $proc = Start-Process `
        -FilePath "cmd.exe" `
        -ArgumentList "/c $tailCommand > `"$logFile`" 2>&1" `
        -WindowStyle Hidden `
        -PassThru

    Start-Sleep -Seconds $DurationSeconds

    if (-not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }

    $lines = @()
    if (Test-Path $logFile) {
        $lines = Get-Content -Path $logFile -ErrorAction SilentlyContinue
        Remove-Item -Path $logFile -Force -ErrorAction SilentlyContinue
    }

    if (-not $lines -or $lines.Count -eq 0) {
        Write-Host "[$timestamp] No log lines captured from log stream. Validation skipped." -ForegroundColor Yellow
        return $true
    }

    $recentLines = $lines | Select-Object -Last $TailLines

    $failureRegex = "(Unauthorized|invalid status 'Unauthorized'|Error booting orchestrator agent|Pre-warm failed|\\b401\\b)"
    $successRegex = "(Application startup complete|Uvicorn running on|Started server process)"

    $failureMatches = $recentLines | Select-String -Pattern $failureRegex
    $successMatches = $recentLines | Select-String -Pattern $successRegex

    if ($failureMatches) {
        Write-Host "[$timestamp] Log validation failed. Found critical lines:" -ForegroundColor Red
        $failureMatches | Select-Object -First 8 | ForEach-Object {
            Write-Host $_.Line -ForegroundColor Red
        }
        return $false
    }

    if ($successMatches) {
        Write-Host "[$timestamp] Log validation passed. Startup markers detected." -ForegroundColor Green
    } else {
        Write-Host "[$timestamp] Log validation found no explicit startup markers, but no auth failures were detected." -ForegroundColor Yellow
    }

    return $true
}

function Refresh-RemoteToken {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] Fetching new Azure access token..." -ForegroundColor Cyan

    $token = az account get-access-token --resource https://ml.azure.com --query accessToken -o tsv
    if (-not $token) {
        throw "Failed to acquire access token. Run 'az login' first."
    }

    if ($UpdateLocalEnv) {
        Update-LocalEnvToken -TokenValue $token
        Write-Host "[$timestamp] Updated local .env token." -ForegroundColor Green
    }

    az webapp config appsettings set `
        --resource-group $ResourceGroup `
        --name $WebAppName `
        --settings AZURE_ACCESS_TOKEN="$token" | Out-Null

    Write-Host "[$timestamp] Updated AZURE_ACCESS_TOKEN on $WebAppName." -ForegroundColor Green

    if ($CheckLogStream) {
        $logOk = Test-RemoteLogStream -DurationSeconds $LogCheckSeconds -TailLines $LogCheckTailLines
        if (-not $logOk) {
            throw "Log stream validation failed after token refresh."
        }
    }
}

if ($Once) {
    Refresh-RemoteToken
    exit 0
}

if ($IntervalMinutes -lt 5) {
    throw "IntervalMinutes must be >= 5."
}

Write-Host "Starting auto-refresh loop every $IntervalMinutes minute(s)." -ForegroundColor Yellow
Write-Host "Resource Group: $ResourceGroup | Web App: $WebAppName" -ForegroundColor Yellow

while ($true) {
    try {
        Refresh-RemoteToken
    } catch {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        Write-Host "[$timestamp] Refresh failed: $($_.Exception.Message)" -ForegroundColor Red
    }

    Start-Sleep -Seconds ($IntervalMinutes * 60)
}
