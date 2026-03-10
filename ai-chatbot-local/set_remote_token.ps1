# 🔄 Azure Token Refresh Script for Chin Hin AI Assistant
# This script automates the 60-minute token refresh for local development.

$ErrorActionPreference = "Stop"

Write-Host "🔐 Fetching new Azure Access Token..." -ForegroundColor Cyan
try {
    # Get a fresh token for the Azure AI Resource scope
    $token = az account get-access-token --resource https://ml.azure.com --query accessToken -o tsv
} catch {
    Write-Host "❌ Failed to get token. Please run 'az login' first." -ForegroundColor Red
    exit 1
}

$envPath = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $envPath)) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    exit 1
}

Write-Host "📝 Updating .env file..." -ForegroundColor Green
$content = Get-Content $envPath
$updated = $false
$newContent = $content | ForEach-Object {
    if ($_ -match "^AZURE_ACCESS_TOKEN=") {
        $updated = $true
        "AZURE_ACCESS_TOKEN=$token"
    } else {
        $_
    }
}

# If the key was not present, append it
if (-not $updated) {
    $newContent += "AZURE_ACCESS_TOKEN=$token"
}

$newContent | Set-Content $envPath
Write-Host "✅ Token refreshed! Valid for ~60 minutes." -ForegroundColor Green
Write-Host "🚀 You can now run: python test_agent.py" -ForegroundColor Cyan

az webapp config appsettings set --resource-group TNT-RG --name tnt-bc5-chatbot-api --settings AZURE_ACCESS_TOKEN="$token"

Write-Host "⏳ Waiting 60 seconds for Azure to stabilize (prevents 502 errors)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

Write-Host "✅ Token set and Azure management plane stabilized." -ForegroundColor Green
