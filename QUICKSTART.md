# 🚀 Chin Hin AI Assistant - Final Quick Start

This guide covers the **Unified Project**: React Native Mobile App + Azure Cloud Backend.

## 📱 Mobile App (Frontend)

The app is configured to connect directly to the **Azure Production API**.

1. **Navigate to Folder**:
   ```powershell
   cd employee-management-mobile
   ```
2. **Install Dependencies**:
   ```powershell
   npm install
   ```
3. **Start the App**:
   ```powershell
   npx expo start
   ```
   - Scan the QR code with your phone (Expo Go app) or press `w` for web.

---

## ☁️ Azure Backend (API)

The backend is hosted at: `https://tnt-bc5-chatbot-api.azurewebsites.net`

### **1. Refresh Local Session (Every 60 mins)**
If you see `Unauthorized` errors while testing locally, run:
```powershell
cd ai-chatbot-local
.\refresh_token.ps1
```

### **2. Permanent Cloud Fix (One-Time Setup)**
To stop the "Unauthorized" errors in the cloud forever, run these commands to authorize the Web App:
```powershell
# Assign AI Developer Role
az role assignment create --assignee decbd200-0b52-4025-83ed-4b418442ab6c --role "Azure AI Developer" --scope /subscriptions/96c8b907-d749-4dec-8c2a-51a334b457bf/resourceGroups/TNT-RG

# Assign Storage Role
az role assignment create --assignee decbd200-0b52-4025-83ed-4b418442ab6c --role "Storage Blob Data Contributor" --scope /subscriptions/96c8b907-d749-4dec-8c2a-51a334b457bf/resourceGroups/TNT-RG
```

### **3. Deploy Updates**
To push new code to Azure:
```powershell
cd ai-chatbot-local
az webapp deploy --name tnt-bc5-chatbot-api --resource-group TNT-RG --src-path deploy.zip --type zip
```

---

## 🎫 UAT Credentials

Use these accounts to test the app:
| Role | Username | Password |
|------|----------|----------|
| Employee | `emp_001` | `password123` |
| HR | `hr_001` | `password123` |
| Admin | `admin_001` | `password123` |

---

## 🛠️ Troubleshooting

### **Unauthorized (401) Error?**
If the chatbot returns "Unauthorized" in the mobile app or web UI, it means the Azure Access Token has expired.

1. **Quick Fix**: 
Run `.\refresh_token.ps1` in the `ai-chatbot-local` folder.
Run this command in PowerShell from the `ai-chatbot-local` directory:

```powershell
# 1. Get a new token and push it to the Azure App Service settings
$token = az account get-access-token --query accessToken -o tsv
az webapp config appsettings set --resource-group TNT-RG --name tnt-bc5-chatbot-api --settings AZURE_ACCESS_TOKEN="$token"

# 2. Hard restart the App Service so the Python worker picks up the new token
az webapp restart --name tnt-bc5-chatbot-api --resource-group TNT-RG
```

2. **Full Guide**: See [AZURE_TOKEN_TROUBLESHOOTING.md](./ai-chatbot-local/AZURE_TOKEN_TROUBLESHOOTING.md) for a step-by-step fix and instructions on how to set up **Managed Identity** (Permanent Fix).

---

## 🏗️ Project Structure
- `employee-management-mobile/`: React Native App (Expo).
- `ai-chatbot-local/`: FastAPI Backend & Agent Logics.
- `ai-chatbot-local/AGENT_PROMPTS/`: AI Behavior Rules.
