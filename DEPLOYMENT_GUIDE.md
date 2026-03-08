# Deployment Guide: Employee Management System

Complete guide to publish the backend API to Azure and mobile apps to iOS App Store and Google Play.

---

## Part 1: Backend (FastAPI) - Azure Deployment

### Current Status
✅ Already deployed at: `https://tnt-bc5-chatbot-api.azurewebsites.net`

### Pre-Deployment Checklist

1. **Update API_BASE_URL in production mode:**
   ```javascript
   // In employee-management-mobile/services/api.js
   // Production should use:
   const API_BASE_URL = 'https://tnt-bc5-chatbot-api.azurewebsites.net/api';
   ```

2. **Verify CORS settings** (already configured in `app/main.py`):
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # Consider restricting in production
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Environment variables check:**
   Ensure these are set in Azure App Service → Configuration:
   - `AZURE_ACCESS_TOKEN` (refreshed via `set_remote_token.ps1`)
   - `DATABASE_URL` (if using PostgreSQL)
   - `PYTHONPATH=/home/site/wwwroot/packages`

### Deploy Backend to Azure

**Command:**
```powershell
cd ai-chatbot-local
.\set_remote_token.ps1
python build_zip.py
az webapp deploy --name tnt-bc5-chatbot-api --resource-group TNT-RG --src-path deploy.zip --type zip
```

**Verify deployment:**
```powershell
curl -s https://tnt-bc5-chatbot-api.azurewebsites.net/debug/auth
```

---

## Part 2: Mobile App - Build & Publish

### Prerequisites

Install required tools:

```bash
# Node.js and npm (required for React Native)
node --version  # Should be v18+
npm --version

# Expo CLI (for building)
npm install -g eas-cli

# Xcode (for iOS) - macOS only
# Download from Mac App Store

# Android Studio (for Android)
# Download from https://developer.android.com/studio
```

### Step 1: Update Production Configuration

**1. Update API endpoint in `employee-management-mobile/services/api.js`:**
```javascript
// Change from local IP to production
const API_BASE_URL = 'https://tnt-bc5-chatbot-api.azurewebsites.net/api';

// In getChatbotBaseUrl():
const getChatbotBaseUrl = () => {
  return 'https://tnt-bc5-chatbot-api.azurewebsites.net';
};
```

**2. Update `app.json` for app store metadata:**
```json
{
  "expo": {
    "name": "Employee Management",
    "slug": "employee-management",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "plugins": [
      [
        "expo-build-properties",
        {
          "ios": {
            "useFrameworks": "static"
          }
        }
      ]
    ],
    "ios": {
      "supportsTabletMode": true,
      "bundleIdentifier": "com.company.employeemanagement"
    },
    "android": {
      "package": "com.company.employeemanagement",
      "versionCode": 1
    }
  }
}
```

---

### Step 2: Build APK for Android

**Option A: Using EAS Build (Recommended - Cloud Build)**

```bash
cd employee-management-mobile

# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Configure EAS
eas build:configure

# Build APK
eas build --platform android --type apk

# Download the APK from the build link provided
```

**Option B: Local Build (Requires Android Studio)**

```bash
cd employee-management-mobile

# Generate APK locally
npx react-native build-android

# Or using Expo:
expo export --platform android
```

---

### Step 3: Build IPA for iOS

**Note: iOS builds REQUIRE a macOS computer**

```bash
cd employee-management-mobile

# Using EAS (Recommended)
eas build --platform ios --type ipa

# Or locally:
expo build:ios
```

---

### Step 4: Publish to App Stores

#### **Google Play (Android)**

1. **Create Google Play account:**
   - Go to https://play.google.com/console
   - Pay $25 registration fee
   - Create new app

2. **Prepare APK:**
   - Get the APK from EAS Build or local build
   - Generate signing key (if not already done):
     ```bash
     eas credentials
     ```

3. **Upload to Google Play:**
   - Open Google Play Console
   - Go to Release → Production
   - Upload the APK/AAB file
   - Fill in app details:
     - App title
     - Short description
     - Full description
     - Screenshots (min 2, max 8)
     - Icon (512x512 PNG)
     - Feature graphic (1024x500 PNG)
   - Set rating and content
   - Submit for review (24-48 hours)

#### **iOS App Store**

1. **Create Apple Developer account:**
   - Go to https://developer.apple.com
   - Pay $99/year membership
   - Create new app in App Store Connect

2. **Prepare IPA:**
   - Get the IPA from EAS Build
   - Certificates will be automatically managed by EAS

3. **Upload to App Store:**
   - Open App Store Connect
   - Go to My Apps → Your App
   - TestFlight → Add Build (for beta testing first)
   - Or directly: App Store → Build → Upload
   - Fill in app details:
     - App name
     - Category
     - Description
     - Keywords
     - Screenshots & previews (for each device size)
     - Icon (1024x1024 PNG)
     - Support URL
     - Privacy Policy URL
   - Set pricing and availability
   - Submit for review (1-3 days)

---

### Step 5: Version Updates

**Update version for new releases:**

```json
// In app.json
{
  "expo": {
    "version": "1.1.0",  // Semver format
    "android": {
      "versionCode": 2    // Increment for each Android release
    }
  }
}
```

**Then rebuild:**
```bash
eas build --platform android --type apk
eas build --platform ios --type ipa
```

---

## Production Checklist

- [ ] Backend API passes all tests
- [ ] API endpoint is `https://tnt-bc5-chatbot-api.azurewebsites.net`
- [ ] Mobile app API_BASE_URL points to production
- [ ] CORS configured (restrict origins if needed)
- [ ] Environment variables set on Azure
- [ ] App icons created (512x512 for Android, 1024x1024 for iOS)
- [ ] Screenshots prepared for store
- [ ] Privacy policy URL added to app
- [ ] App description and keywords finalized
- [ ] Testing completed on physical devices
- [ ] Signed APK/IPA generated
- [ ] Google Play and App Store accounts created
- [ ] Developer fees paid
- [ ] Apps submitted for review

---

## Quick Reference Commands

```bash
# Build backend
cd ai-chatbot-local
python build_zip.py
az webapp deploy --name tnt-bc5-chatbot-api --resource-group TNT-RG --src-path deploy.zip --type zip

# Build Android (cloud)
cd employee-management-mobile
eas build --platform android --type apk

# Build iOS (cloud)
eas build --platform ios --type ipa

# Update app version
# Edit app.json, then rebuild
```

---

## Support & Troubleshooting

**iOS build fails:**
- Ensure macOS is used or use EAS Build
- Check Xcode version: `xcode-select --version`

**Android build fails:**
- Ensure Android SDK is installed
- Check `ANDROID_SDK_ROOT` environment variable
- Update Gradle: `./gradlew --version`

**App rejected by stores:**
- Check store guidelines (App Store Review Guidelines, Google Play policies)
- Ensure privacy policy is accessible
- Test app thoroughly on multiple devices
- Check for hardcoded credentials or sensitive data

---

**Last Updated:** March 2026
