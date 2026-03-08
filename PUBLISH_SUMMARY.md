# Publishing Project: Quick Summary

This document summarizes the steps to publish both the backend API and mobile app.

---

## 📱 Project Structure

```
Chin Hin Hackathon/Business Challenge 5/
├── ai-chatbot-local/          ← FastAPI Backend
│   ├── app/main.py           (Already deployed to Azure)
│   ├── requirements.txt
│   ├── build_zip.py
│   └── set_remote_token.ps1
│
├── employee-management-mobile/ ← React Native Mobile App
│   ├── package.json
│   ├── app.json              (Updated for production)
│   ├── eas.json              (Build configuration)
│   ├── services/api.js       (Updated to use Azure backend)
│   └── BUILD_AND_PUBLISH.md  (Detailed guide)
│
├── DEPLOYMENT_GUIDE.md        (Full deployment instructions)
└── PUBLISH_SUMMARY.md         (This file)
```

---

## 🚀 Quick Steps to Publish

### Part 1: Backend (Already Done ✅)
- FastAPI app deployed to: **https://tnt-bc5-chatbot-api.azurewebsites.net**
- No additional backend publishing needed when you deploy with:
  ```powershell
  cd ai-chatbot-local
  .\set_remote_token.ps1
  python build_zip.py
  az webapp deploy --name tnt-bc5-chatbot-api --resource-group TNT-RG --src-path deploy.zip --type zip
  ```

### Part 2: Mobile App (Android & iOS)

#### Prerequisites (First Time Only)
```bash
# Install build tools
npm install -g eas-cli

# Login to Expo
eas login  # Create account at https://expo.dev (free)
```

eas init

#### Build for Android & iOS
```bash
cd employee-management-mobile

# Build Android APK (cloud build)
eas build --platform android --profile production

# Build iOS IPA (cloud build)
# You must get Apple Deverloper Account first
eas build --platform ios --profile production
```
Both commands output download links to APK and IPA.

#### Publish to App Stores

**Google Play (Android):**
1. Create Google Play Developer account ($25 fee): https://play.google.com/console
2. Create app in Google Play Console
3. Upload APK file
4. Add app icon, screenshots, description
5. Submit for review (24-48 hours)

**App Store (iOS):**
1. Create Apple Developer account ($99/year): https://developer.apple.com
2. Create app in App Store Connect: https://appstoreconnect.apple.com
3. Upload IPA file
4. Add app icon, screenshots, description
5. Submit for review (1-3 days)

---

## 📋 Pre-Publishing Checklist

### Backend
- [ ] Azure app service is running
- [ ] Environment variables are set on Azure
- [ ] API endpoint responds: `https://tnt-bc5-chatbot-api.azurewebsites.net/debug/auth`

### Mobile App
- [ ] `app.json` updated with proper iOS/Android bundle IDs
- [ ] `services/api.js` uses production backend URL
- [ ] All credentials removed from code
- [ ] Privacy policy URL available
- [ ] Support email configured
- [ ] App icons ready (1024x1024 PNG for iOS, 512x512 for Android)
- [ ] Screenshots prepared (min 2-3 per platform)

---

## 📚 Detailed Documentation

- **Full Backend Guide:** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Mobile Build Guide:** See [employee-management-mobile/BUILD_AND_PUBLISH.md](employee-management-mobile/BUILD_AND_PUBLISH.md)

---

## 🔗 Important Links

| Service | URL | Purpose |
|---------|-----|---------|
| Backend API | https://tnt-bc5-chatbot-api.azurewebsites.net | FastAPI server |
| Google Play Console | https://play.google.com/console | Android publishing |
| App Store Connect | https://appstoreconnect.apple.com | iOS publishing |
| Expo Account | https://expo.dev | Mobile build service |
| GitHub Copilot Deploy | https://github.com/copilot/deploy | CI/CD helper |

---

## ⚡ Common Commands

```bash
# Mobile app build & test
cd employee-management-mobile
npm install                      # Install dependencies
npm start                        # Start dev server
eas build --platform android     # Build Android
eas build --platform ios        # Build iOS

# Backend deployment
cd ai-chatbot-local
python build_zip.py             # Create deployment package
az webapp deploy --name tnt-bc5-chatbot-api --resource-group TNT-RG --src-path deploy.zip --type zip
```

---

## 📞 Support

- **Expo Documentation:** https://docs.expo.dev
- **Google Play Help:** https://support.google.com/googleplay
- **App Store Help:** https://help.apple.com/app-store-connect

---

**Status:** Ready for publication ✅
**Last Updated:** March 7, 2026
