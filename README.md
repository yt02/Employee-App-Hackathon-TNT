# Chin Hin Employee Management System

A comprehensive employee management solution featuring an AI-powered chatbot backend and a cross-platform mobile application. Built for Chin Hin employees to manage leave, book meeting rooms, and handle IT support tickets through natural language conversations.

## 🏗️ Architecture Overview

This project consists of two main components:

### 🤖 AI Chatbot Backend (`ai-chatbot-local/`)
- **Framework**: FastAPI with Python
- **AI Engine**: Microsoft Azure AI Foundry Agent
- **Features**: 
  - Leave management (apply, check balance)
  - Meeting room booking
  - IT support ticket creation and tracking
  - RAG (Retrieval-Augmented Generation) for document-based queries
- **Deployment**: Azure Web App

### 📱 Mobile Application (`employee-management-mobile/`)
- **Framework**: React Native with Expo
- **Features**:
  - AI Assistant with rich chat interface
  - Leave management dashboard
  - Meeting room booking system
  - Attendance tracking
  - Support ticket management
- **Platforms**: iOS, Android, Web

## 🚀 Quick Start

### Prerequisites

Before getting started, ensure you have the following installed:

1. **Azure CLI** (Required for deployment and authentication)
   - Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
   - For Windows: Download the MSI installer and run it
   - Verify installation: Open PowerShell and run `az --version`

2. **Git** (For version control)
   - Download from: https://git-scm.com/downloads
   - Install with default settings

3. **Python 3.10+** (For backend development)
   - Download from: https://www.python.org/downloads/
   - Add to PATH during installation

4. **Node.js 18+** (For mobile app development)
   - Download from: https://nodejs.org/
   - Includes npm package manager

5. **Expo CLI** (For React Native development)
   ```bash
   npm install -g @expo/cli
   ```

### Installation and Setup

#### 1. Clone the Repository
```bash
git clone <your-github-repo-url>
cd "Business Challenge 5"
```

#### 2. Backend Setup (AI Chatbot)

Navigate to the backend folder:
```bash
cd ai-chatbot-local
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Set up environment variables:
- Copy `.env.example` to `.env`
- Fill in your Azure AI Foundry credentials and other required variables

For local development:
```bash
python app/main.py
```

#### 3. Mobile App Setup

Navigate to the mobile app folder:
```bash
cd ../employee-management-mobile
```

Install dependencies:
```bash
npm install
```

Start the development server:
```bash
npx expo start
```

- For iOS/Android: Scan QR code with Expo Go app
- For Web: Press `w` in terminal

### Azure Deployment

#### Backend Deployment

1. **Login to Azure CLI**:
   ```bash
   az login
   ```

2. **Build and Deploy**:
   ```bash
   cd ai-chatbot-local
   python build_zip.py
   az webapp deploy --name <your-webapp-name> --resource-group <your-resource-group> --src-path deploy.zip --type zip
   ```

3. **Configure Permissions** (One-time setup):
   ```bash
   # Assign AI Developer Role
   az role assignment create --assignee <your-app-service-principal-id> --role "Azure AI Developer" --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>

   # Assign Storage Blob Data Contributor Role
   az role assignment create --assignee <your-app-service-principal-id> --role "Storage Blob Data Contributor" --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>
   ```

#### Mobile App Deployment

1. **Build for Production**:
   ```bash
   cd employee-management-mobile
   eas build --platform ios --profile production
   # or
   eas build --platform android --profile production
   ```

2. **Submit to App Stores**:
   - iOS: Use `eas submit` or upload to App Store Connect
   - Android: Use `eas submit` or upload to Google Play Console

## 📁 Project Structure

```
Business Challenge 5/
├── ai-chatbot-local/          # Python FastAPI backend
│   ├── app/                   # Main application code
│   ├── data/                  # Mock data and documents
│   ├── requirements.txt       # Python dependencies
│   └── README.md             # Backend-specific documentation
├── employee-management-mobile/ # React Native mobile app
│   ├── assets/               # Images and media files
│   ├── screens/              # App screens/components
│   ├── services/             # API services
│   ├── package.json          # Node dependencies
│   └── README.md            # Mobile app documentation
├── QUICKSTART.md             # Unified quick start guide
├── DEPLOYMENT_GUIDE.md       # Detailed deployment instructions
└── README.md                # This file
```

## 🔧 Development

### Backend Development
- **Local Testing**: Run `python app/main.py`
- **API Documentation**: Visit `http://localhost:8000/docs` for Swagger UI
- **Environment**: Create virtual environment with `python -m venv venv`

### Mobile Development
- **Hot Reload**: Changes reflect instantly with Expo
- **Debugging**: Use React Native Debugger or Flipper
- **Testing**: Run `npm test` for unit tests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add your feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Submit a pull request

## 📄 License

This project is proprietary software for Chin Hin organization.

## 🆘 Support

For support and questions:
- Check the individual README files in each component folder
- Review the QUICKSTART.md for common issues
- Contact the development team

---

**Built with ❤️ for Chin Hin Employees**