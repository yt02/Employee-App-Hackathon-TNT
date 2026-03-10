# 🔐 Authentication Fix for Microsoft Foundry Agent

## ❌ The Problem

The error you're seeing:
```
DefaultAzureCredential failed to retrieve a token from the included credentials
```

This happens because `AIProjectClient` **ONLY** supports `DefaultAzureCredential()` authentication, which requires one of these methods:
- Azure CLI (`az login`)
- Environment variables (AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET)
- Managed Identity (when running on Azure)
- Visual Studio Code authentication

**API Key authentication is NOT supported by `AIProjectClient`.**

---

## ✅ Solution: Use Azure CLI (Recommended)

### **Step 1: Install Azure CLI**

**For Windows:**
Download and install from: https://aka.ms/installazurecliwindows

Or use PowerShell:
```powershell
winget install -e --id Microsoft.AzureCLI
```

Or use Chocolatey:
```powershell
choco install azure-cli
```

### **Step 2: Login to Azure**

```powershell
az login
```

This will open a browser window for you to login. Once logged in, the authentication will be cached and `DefaultAzureCredential()` will work automatically.

> [!TIP]
> **New Automation**: You can now use `.\refresh_token.ps1` to automatically update your `.env` file with a fresh token whenever it expires.

### **Step 3: Verify Authentication**

```powershell
az account show
```

You should see your Azure subscription details.

### **Step 4: Test the Agent**

```powershell
cd ai-chatbot-local
python test_agent.py
```

### **Step 5: Run the Chatbot**

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

---

## 🔄 Alternative Solution: Use Environment Variables

If you can't install Azure CLI, you can use a Service Principal with environment variables:

### **Step 1: Create a Service Principal**

```powershell
az ad sp create-for-rbac --name "my-chatbot-sp" --role Contributor --scopes /subscriptions/{subscription-id}
```

This will output:
```json
{
  "appId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "displayName": "my-chatbot-sp",
  "password": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "tenant": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

### **Step 2: Add to .env File**

```env
AZURE_CLIENT_ID=<appId from above>
AZURE_TENANT_ID=<tenant from above>
AZURE_CLIENT_SECRET=<password from above>

AZURE_CONNECTION_STRING=eastus2.api.azureml.ms;96c8b907-d749-4dec-8c2a-51a334b457bf;TNT-RG;tnt-bc5-employee-app
AZURE_AGENT_ID=asst_C7uSyxWNjSPXiVj5TIhAOIe3
```

### **Step 3: Test**

```powershell
python test_agent.py
```

---

## 🚫 Why API Key Doesn't Work

According to Microsoft documentation:
> "The Azure AI Project Client (`AIProjectClient`) does not support API Key authentication. Instead, it is designed to work with Managed Identities or `DefaultAzureCredential()` for authentication."

Source: https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme

---

## 📋 Summary

| Method | Difficulty | Recommended |
|--------|-----------|-------------|
| **Azure CLI (`az login`)** | Easy | ✅ **YES** |
| **Environment Variables** | Medium | ⚠️ If CLI not available |
| **API Key** | N/A | ❌ **NOT SUPPORTED** |

---

## 🎯 Quick Start (Recommended Path)

```powershell
# 1. Install Azure CLI
winget install -e --id Microsoft.AzureCLI

# 2. Login
az login

# 3. Test the agent
cd ai-chatbot-local
python test_agent.py

# 4. Run the chatbot
python -m uvicorn app.main:app --reload --port 8000
```

---

## 🐛 Still Having Issues?

If you still get authentication errors after `az login`:

1. **Check your Azure subscription:**
   ```powershell
   az account list
   ```

2. **Set the correct subscription:**
   ```powershell
   az account set --subscription "<your-subscription-id>"
   ```

3. **Verify you have access to the resource:**
   ```powershell
   az resource show --ids /subscriptions/96c8b907-d749-4dec-8c2a-51a334b457bf/resourceGroups/TNT-RG/providers/Microsoft.MachineLearningServices/workspaces/tnt-bc5-employee-app
   ```

---

**The easiest solution is to install Azure CLI and run `az login`!** 🚀

