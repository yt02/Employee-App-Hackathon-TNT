# AI Chatbot Flutter App

A mobile app for the AI Chatbot powered by Microsoft Foundry Agent. Built with Flutter for cross-platform support (iOS, Android, Windows, Web).

## 🚀 Features

- 💬 Real-time chat with AI agent
- 📱 Works on phone and laptop simultaneously
- 🎨 Material Design 3 with light/dark theme support
- 💾 Clean architecture with Provider state management
- 🔄 Auto-scroll to latest messages
- 🗑️ Clear chat history

## 📋 Prerequisites

1. **Flutter SDK** - [Install Flutter](https://docs.flutter.dev/get-started/install)
2. **Backend running** - The FastAPI chatbot backend must be running
3. **Same network** - Phone and laptop must be on the same WiFi network

## 🛠️ Setup Instructions

### 1. Install Flutter Dependencies

```bash
cd ai-chatbot-flutter
flutter pub get
```

### 2. Update API Base URL

Open `lib/services/api_service.dart` and update the IP address to your computer's IP:

```dart
static const String baseUrl = 'http://YOUR_COMPUTER_IP:8000';
```

**Find your IP address:**
- Windows: `ipconfig` (look for IPv4 Address)
- Mac/Linux: `ifconfig` (look for inet)

### 3. Start the Backend

In a separate terminal:

```bash
cd ai-chatbot-local
python -m uvicorn app.main:app --reload --port 8000 --host 0.0.0.0
```

**Important:** Use `--host 0.0.0.0` to allow connections from your phone!

### 4. Run the Flutter App

**On your phone:**
```bash
flutter run
```

**On your laptop (Windows):**
```bash
flutter run -d windows
```

**On your laptop (Web):**
```bash
flutter run -d chrome
```

**Run on multiple devices simultaneously:**
```bash
# Terminal 1: Run on phone
flutter run

# Terminal 2: Run on Windows
flutter run -d windows
```

## 📱 Testing on Phone

1. **Connect phone via USB** (for Android) or **same WiFi** (for iOS/Android)
2. **Enable USB debugging** (Android only)
3. **Run `flutter devices`** to see available devices
4. **Run `flutter run`** and select your phone

## 🌐 Network Configuration

For the app to work on your phone:

1. ✅ Phone and laptop on **same WiFi network**
2. ✅ Backend running with `--host 0.0.0.0`
3. ✅ Firewall allows port 8000 (Windows Firewall may block it)
4. ✅ Correct IP address in `api_service.dart`

**Test connectivity from phone:**
- Open browser on phone
- Go to `http://YOUR_COMPUTER_IP:8000/docs`
- You should see the FastAPI docs page

## 🔧 Troubleshooting

### "Failed to connect to server"

1. Check backend is running: `curl http://localhost:8000/chat -X POST -H "Content-Type: application/json" -d "{\"message\": \"test\"}"`
2. Check firewall settings (Windows Defender may block port 8000)
3. Verify IP address is correct
4. Ensure phone and laptop are on same network

### "No devices found"

**For Android:**
- Enable USB debugging in Developer Options
- Accept USB debugging prompt on phone
- Run `flutter doctor` to check setup

**For iOS:**
- Install Xcode (Mac only)
- Trust the computer on your iPhone
- Run `flutter doctor` to check setup

### Backend not accessible from phone

**Windows Firewall:**
```powershell
# Allow port 8000 through firewall
netsh advfirewall firewall add rule name="FastAPI" dir=in action=allow protocol=TCP localport=8000
```

## 📂 Project Structure

```
ai-chatbot-flutter/
├── lib/
│   ├── main.dart                 # App entry point
│   ├── models/
│   │   └── message.dart          # Message data model
│   ├── providers/
│   │   └── chat_provider.dart    # State management
│   ├── screens/
│   │   └── chat_screen.dart      # Main chat screen
│   ├── services/
│   │   └── api_service.dart      # API communication
│   └── widgets/
│       ├── message_bubble.dart   # Message UI component
│       └── message_input.dart    # Input field component
└── pubspec.yaml                  # Dependencies
```

## 🎨 Customization

### Change Theme Colors

Edit `lib/main.dart`:

```dart
colorScheme: ColorScheme.fromSeed(
  seedColor: Colors.purple, // Change this color
  brightness: Brightness.light,
),
```

### Change API Endpoint

Edit `lib/services/api_service.dart`:

```dart
static const String baseUrl = 'http://YOUR_IP:YOUR_PORT';
```

## 📝 Notes

- The app uses Material Design 3 for modern UI
- State management with Provider pattern
- HTTP package for API requests
- Auto-scrolls to latest messages
- Supports light and dark themes based on system settings

## 🚀 Quick Start Summary

```bash
# 1. Install dependencies
cd ai-chatbot-flutter
flutter pub get

# 2. Update IP in lib/services/api_service.dart

# 3. Start backend (in another terminal)
cd ../ai-chatbot-local
python -m uvicorn app.main:app --reload --port 8000 --host 0.0.0.0

# 4. Run on phone
flutter run

# 5. Run on laptop (optional - in another terminal)
flutter run -d windows
```

Enjoy your AI Chatbot! 🎉

