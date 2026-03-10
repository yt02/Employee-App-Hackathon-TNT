# Build and Publish Guide for Employee Management Mobile App

This guide covers building APK for Android and IPA for iOS, then publishing to app stores.

## Prerequisites

### Global Setup
```bash
# Install Node.js (v18+)
node --version

# Install EAS CLI for building
npm install -g eas-cli

# Login to Expo (create account at https://expo.dev)
eas login
```

### For Android & Google Play
- Google Play Developer account ($25 one-time fee)
- Google Play Console: https://play.google.com/console

### For iOS & App Store
- Apple Developer account ($99/year)
- App Store Connect: https://appstoreconnect.apple.com
- macOS computer (Xcode required for local builds)

---

## Quick Start

### 1. Configure EAS Build

```bash
cd employee-management-mobile

# First time setup
eas build:configure

# This creates eas.json with build configuration
```

### 2. Build for Android (APK)

**Cloud Build (Recommended - No local Android SDK needed):**
```bash
eas build --platform android --type apk
```

Output: Download link to APK file

**Local Build (Requires Android Studio):**
```bash
# Ensure you have Android SDK set up
npx react-native build-android --mode=release
```

### 3. Build for iOS (IPA)

**Cloud Build (Recommended - Works from any OS):**
```bash
eas build --platform ios --type ipa
```

**Local Build (macOS only):**
```bash
eas build --platform ios --type ipa
```

---

## Publishing Steps

### Step 1: Prepare App Store Assets

Create these before publishing:

**Android Google Play:**
- ✅ App icon (512x512 PNG)
- ✅ Feature graphic (1024x500 PNG)
- ✅ Screenshots (min 2, max 8 for phones)
- ✅ App title (50 chars max)
- ✅ Short description (80 chars max)
- ✅ Full description (4000 chars max)
- ✅ Privacy policy URL
- ✅ Support contact email

**iOS App Store:**
- ✅ App icon (1024x1024 PNG)
- ✅ Screenshots (for each device size)
- ✅ App name (30 chars max)
- ✅ Subtitle (30 chars max)
- ✅ Description (4000 chars max)
- ✅ Privacy policy URL
- ✅ Support URL
- ✅ Marketing URL (optional)

### Step 2: Upload to Google Play

1. **Open Google Play Console:**
   ```
   https://play.google.com/console
   ```

2. **Create App:**
   - Click "Create app"
   - App name: "Employee Management"
   - Default language: English
   - App category: Business
   - Create as free or paid

3. **Upload APK:**
   - Go to Release → Testing → Internal testing
   - Click "Create new release"
   - Upload the APK file from EAS build
   - Add release notes
   - Click "Save & review"

4. **Add Store Listing:**
   - App details → Title & description
   - Screenshots (minimum 2)
   - Icon (512x512)
   - Feature graphic (1024x500)
   - Category and content rating

5. **Set Pricing:**
   - App pricing → Free
   - Distribution → Select countries

6. **Submit for Review:**
   - Once all sections complete, submit for review
   - Expected review time: 1-2 hours for initial review, then 24-48 hours for app store

---

### Step 3: Upload to iOS App Store

1. **Open App Store Connect:**
   ```
   https://appstoreconnect.apple.com
   ```

2. **Create App:**
   - Click "My Apps" → "+"
   - Select "New App"
   - Platform: iOS
   - App name: "Employee Management"
   - Bundle ID: `com.hackathon.employeemanagement` (must match app.json)
   - SKU: `emp-mgmt-001`
   - Availability: Select countries

3. **Upload IPA:**
   - TestFlight → "Build" → Upload new build
   - Choose the IPA from EAS build
   - Wait for processing (usually 5-10 mins)

4. **Test with TestFlight (Optional but recommended):**
   - Add internal testers
   - Get feedback before submitting to App Store
   - Minimum 1 internal test to proceed

5. **Add App Store Information:**
   - App Information → Name, Subtitle, Description
   - Choose appropriate category
   - Privacy policy URL required

6. **Add Screenshots:**
   - All Devices section
   - Add screenshots for each device type (iPhone, iPad)
   - Minimum 2 screenshots per device
   - Max 10 screenshots

7. **Submit for Review:**
   - Build → Select your build
   - Add export information (encryption, compliance)
   - Submit for Review
   - Expected review time: 1-3 business days

---

## Version Updates

### Updating to Next Version (e.g., 1.0.1)

#### Step 1: Update version in code
```json
// app.json
{
  "expo": {
    "version": "1.0.1",
    "android": {
      "versionCode": 2  // Increment for each Android release
    }
  }
}
```

#### Step 2: Rebuild
```bash
eas build --platform android --type apk
eas build --platform ios --type ipa
```

#### Step 3: Upload new build to stores
- Google Play: Create new release with updated APK
- App Store: Upload new build, then submit for review

---

## Troubleshooting

### Build Fails with "Credentials not configured"
```bash
# Reset credentials
eas credentials

# Or create new ones
eas credentials --platform android
eas credentials --platform ios
```

### App rejected by Google Play
Common reasons:
- Missing or invalid privacy policy URL
- App crashes on launch
- Insufficient content (description too short)
- Violates Play Store policies

Solution:
- Fix the issue
- Build new APK (version code +1)
- Upload new build and resubmit

### App rejected by App Store
Common reasons:
- Contains hardcoded credentials
- Requires user account without clear value
- Excessive ads or push notifications
- Accessing features without permission

Solution:
- Review Apple's App Store Review Guidelines
- Remove/fix issues
- Build new IPA
- Submit new build with detailed explanation (if needed)

### IPA Upload Fails on Mac
```bash
# Try using Transporter app
# Download: https://apps.apple.com/us/app/transporter/id1450874784

# Then drag & drop the IPA file into Transporter
```

---

## Monitor App Performance

### Google Play
- Go to Reports → Statistics
- Track installs, ratings, crashes

### App Store
- App Analytics → Trends
- Monitor downloads, crashes, ratings

---

## Support Resources

- **Expo Build Documentation:** https://docs.expo.dev/build/
- **Google Play Console Help:** https://support.google.com/googleplay/android-developer/
- **App Store Connect Help:** https://help.apple.com/app-store-connect/
- **React Native Documentation:** https://reactnative.dev/

---

**Last Updated:** March 2026
