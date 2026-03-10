# AI Chatbot - Microsoft Foundry Agent Integration

This chatbot has been updated to use **Microsoft Foundry Agent** instead of Google's Vertex AI.

## 🔄 What Changed

### **Before (Google Vertex AI)**
- Used Google Gemini API
- Required VERTEX_API_KEY
- Used RAG (Retrieval Augmented Generation) with vector store
- Complex setup with embeddings and document retrieval

### **After (Microsoft Foundry Agent)**
- Uses Azure AI Projects SDK
- Connects to pre-configured Microsoft Foundry agent
- Simpler integration - agent handles all the logic
- No need for local vector store or embeddings

---

## 🚀 Setup Instructions

### **1. Install Dependencies**

```bash
cd ai-chatbot-local
pip install -r app/requirements.txt
```

This will install:
- `azure-ai-projects==1.0.0b10` - Azure AI Projects SDK
- `azure-identity` - Azure authentication
- `fastapi` - Web framework
- `uvicorn` - ASGI server

### **2. Configure Environment Variables**

Create a `.env` file in the `ai-chatbot-local` directory:

```bash
cp .env.example .env
```

The `.env` file should contain:

```env
AZURE_CONNECTION_STRING=eastus2.api.azureml.ms;96c8b907-d749-4dec-8c2a-51a334b457bf;TNT-RG;tnt-bc5-employee-app
AZURE_AGENT_ID=asst_C7uSyxWNjSPXiVj5TIhAOIe3
```

### **3. Azure Authentication**

The agent uses `DefaultAzureCredential()` which tries multiple authentication methods:

1. **Environment variables** (AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET)
2. **Managed Identity** (if running on Azure)
3. **Azure CLI** (if logged in via `az login`)
4. **Visual Studio Code** (if logged in)
5. **Azure PowerShell** (if logged in)

**Recommended for local development:**

```bash
# Install Azure CLI if not already installed
# Then login:
az login
```

### **4. Run the Chatbot**

```bash
cd ai-chatbot-local
python -m uvicorn app.main:app --reload --port 8000
```

Then open: http://localhost:8000

---

## 📁 File Structure

```
ai-chatbot-local/
├── app/
│   ├── main.py              # FastAPI app (unchanged)
│   ├── chat.py              # Updated to use Azure agent
│   ├── azure_agent.py       # NEW: Microsoft Foundry agent integration
│   ├── config.py            # Updated with Azure config
│   ├── requirements.txt     # Updated dependencies
│   └── static/
│       ├── index.html       # Chat UI (unchanged)
│       └── script.js        # Frontend (unchanged)
├── .env                     # Your environment variables
└── .env.example             # Example configuration
```

---

## 🔧 How It Works

### **1. User sends a message**
Frontend (`script.js`) → POST `/chat` → `main.py`

### **2. Backend processes the message**
`main.py` → `chat.ask()` → `azure_agent.ask_agent()`

### **3. Azure agent responds**
```python
# Create a thread
thread = client.agents.create_thread()

# Send user message
message = client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content=question
)

# Run the agent
run = client.agents.create_and_process_run(
    thread_id=thread.id,
    agent_id=agent.id
)

# Get response
messages = client.agents.list_messages(thread_id=thread.id)
```

### **4. Response sent back to user**
`azure_agent.py` → `chat.py` → `main.py` → Frontend

---

## 🧪 Testing

### **Test the API directly:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hi Agent165"}'
```

Expected response:
```json
{
  "answer": "Hello! How can I help you today?"
}
```

---

## 🐛 Troubleshooting

### **Error: "DefaultAzureCredential failed to retrieve a token"**

**Solution:** Login with Azure CLI:
```bash
az login
```

### **Error: "Agent not found"**

**Solution:** Check that `AZURE_AGENT_ID` in `.env` is correct:
```env
AZURE_AGENT_ID=asst_C7uSyxWNjSPXiVj5TIhAOIe3
```

### **Error: "Connection string invalid"**

**Solution:** Verify `AZURE_CONNECTION_STRING` format:
```env
AZURE_CONNECTION_STRING=eastus2.api.azureml.ms;96c8b907-d749-4dec-8c2a-51a334b457bf;TNT-RG;tnt-bc5-employee-app
```

---

## 📝 Notes

- The old RAG files (`rag.py`, vector store) are no longer used but kept for reference
- The agent is configured in Microsoft Foundry portal
- Each conversation creates a new thread (stateless)
- For production, consider implementing thread persistence for conversation history

---

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Configure `.env` file
3. ✅ Login with Azure CLI (`az login`)
4. ✅ Run the chatbot
5. ✅ Test in browser

**Your chatbot is now powered by Microsoft Foundry Agent!** 🚀

