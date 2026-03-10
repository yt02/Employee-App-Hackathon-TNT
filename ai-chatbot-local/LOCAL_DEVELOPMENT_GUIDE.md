# 💻 Local Development & Mobile Testing Guide

This guide explains how to run the backend server on your **local machine** so you can test it with the mobile application before deploying to Azure.

## 📋 Prerequisites
- **Python 3.10 or 3.11** installed on your system.
- Your mobile device and your computer must be on the **same Wi-Fi network**.

---

## 🛠️ Step 1: Set Up Python Environment

Open a terminal (PowerShell or CMD) in the project root:

```powershell
# 1. Create a virtual environment
python -m venv venv

# 2. Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 🔑 Step 2: Configure Environment Variables

1. Ensure you have a `.env` file in the root directory.
2. The server needs a valid **Azure Access Token** to call the AI Agents locally.
3. Use the following command to refresh your local token:
   ```powershell
   .\set_remote_token.ps1
   ```
   *This script fetches a token and updates your `.env` automatically.*

---

## 🌐 Step 3: Find Your Local IP Address

To allow your mobile phone to "see" your computer, you must use your computer's **Local IP**, not `localhost`.

1. Run `ipconfig` in your terminal.
2. Look for **IPv4 Address** (likely something like `192.168.1.XX`).
3. Make a note of this address.

---

## 🚀 Step 4: Run the Server

Run the server and bind it to `0.0.0.0` (this makes it accessible to other devices on the network):

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📱 Step 5: Connect Your Mobile App

1. Open your mobile application code.
2. Locate the **API URL** configuration.
3. Change it from the Azure URL to your local IP:
   - **From:** `https://tnt-bc5-chatbot-api.azurewebsites.net`
   - **To:** `http://192.168.1.XX:8000` (Replace `192.168.1.XX` with your actual IP)
4. Build and run your mobile app.

---

## 💡 Troubleshooting Tips

- **Firewall:** If your mobile app cannot connect, ensure your Windows Firewall allows inbound traffic on port `8000`.
- **Token Expired:** The Azure token lasts for ~60 minutes. If the chatbot starts replying with errors, run `.\set_remote_token.ps1` again.
- **SSL:** Note that local development uses `http`, while Azure uses `https`. Ensure your mobile app configurations allow non-HTTPS traffic for development builds.
