# Refresh Token Guide (Non-Technical)

This guide helps you refresh the Azure token so the mobile app can keep working.

## When should I do this?

Refresh the token when:
- The app shows `Unauthorized` or network error
- The chatbot stops responding properly
- You know the token has expired (usually around 1 hour)

## Before you start

You need:
- A Windows laptop
- Internet connection
- Azure CLI installed
- Access to the folder that contains these scripts:
  - `auto_refresh_remote_token.ps1`
  - `install_token_refresh_task.ps1`
  - `remove_token_refresh_task.ps1`

## How to open the correct folder (any device)

1. Open **File Explorer**
2. Go to your project folder
3. Open the `ai-chatbot-local` folder
4. In that folder, click the address bar, type `powershell`, then press **Enter**

PowerShell will open in the correct location.

## Option A (Recommended): Run once now

1. Open **PowerShell** (windows key + R, type `powershell` and press enter)
2. Copy and run:

```powershell
az login
powershell -ExecutionPolicy Bypass -File .\auto_refresh_remote_token.ps1 -Once -CheckLogStream -LogCheckSeconds 45
```

3. Wait until you see a success message in green.

This updates the token in Azure App Service and checks logs for common errors.

## Option B: Run every 1 hour automatically

1. Open **PowerShell**
2. Copy and run:

```powershell
az login
powershell -ExecutionPolicy Bypass -File .\install_token_refresh_task.ps1 -LogCheckSeconds 45
```

3. Done. Windows Task Scheduler will run it every hour.

## Important warning

If your laptop is **sleeping** or **powered off**, automatic refresh will not run.

To reduce issues:
- Keep laptop plugged in
- Set Sleep to `Never` (while charging)

## If token still fails

Run this to restart the Azure web app:

```powershell
az webapp restart --resource-group TNT-RG --name tnt-bc5-chatbot-api
```

Then run Option A again.

## Remove hourly auto-refresh (if needed)

```powershell
powershell -ExecutionPolicy Bypass -File .\remove_token_refresh_task.ps1
```
