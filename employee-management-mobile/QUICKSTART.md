# 🚀 Quick Start Guide (Mobile + Cloud)

This guide covers how to run the mobile app connected to the **Azure Production API**.

## Step 1: Verify API Configuration

The mobile app is pre-configured to connect to:
`https://tnt-bc5-chatbot-api.azurewebsites.net`

You do **not** need to change `services/api.js` unless you are testing locally.

## Step 2: Start Mobile App

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

## Step 3: Open on iPhone/Android

1. Download **Expo Go** from App Store or Play Store.
2. Scan the QR code from your terminal.

## Step 4: Login

Use any of these demo accounts:
- Username: `emp_001` | Password: `password123`
- Username: `hr_001` | Password: `password123`
- Username: `admin_001` | Password: `password123`

## 🔧 Troubleshooting

### **Unauthorized (401) Error?**
If the chatbot returns "Unauthorized", the Azure cloud token has expired.

1. **Quick Fix**: Run `.\refresh_token.ps1` in the `ai-chatbot-local` folder.
2. **Detailed Help**: See [AZURE_TOKEN_TROUBLESHOOTING.md](../ai-chatbot-local/AZURE_TOKEN_TROUBLESHOOTING.md).

### **App won't load?**
- Ensure your phone and computer are on the same WiFi (only required if testing locally).
- Try `npm start -- --clear`.

---
enjoy the premium experience! 🎉
