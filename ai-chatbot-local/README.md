# 🤖 Chin Hin Employee Assistant

> AI-powered employee management chatbot built with **FastAPI** and **Microsoft Azure AI Foundry Agent**.  
> Employees can manage leave, book meeting rooms, and raise IT tickets through natural conversation.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi&logoColor=white)
![Azure AI](https://img.shields.io/badge/Azure_AI_Foundry-Agent-0078D4?logo=microsoftazure&logoColor=white)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📅 **Leave Management** | Check balance, apply for annual / medical / unpaid leave |
| 🏢 **Meeting Rooms** | Browse available rooms, book by date & time |
| 🎫 **IT Support Tickets** | Create tickets (hardware, software, network), check status |
| 🧠 **AI Function Calling** | Azure AI Agent decides *when* to call tools — no rigid keyword matching |
| 🎨 **Premium Dark UI** | Responsive chat interface with sidebar, suggestion chips, and animations |

---

## 📁 Project Structure

```
ai-chatbot-local/
├── app/
│   ├── main.py              # FastAPI app, routes, static‑file serving
│   ├── chat.py              # Routes user messages → Azure AI Agent
│   ├── azure_agent.py       # Azure AI Foundry agent integration
│   ├── tools.py             # Function Tool definitions for the agent
│   ├── config.py            # Environment variable loading
│   ├── rag.py               # RAG / vector‑store utilities (Gemini embeddings)
│   ├── modules/
│   │   ├── leave_manager.py
│   │   ├── room_manager.py
│   │   └── ticket_manager.py
│   ├── static/
│   │   ├── index.html
│   │   ├── style.css
│   │   └── script.js
│   └── requirements.txt
├── data/
│   ├── mock_data/            # JSON files (users, rooms, tickets, etc.)
│   └── docs_data/            # PDF documents for RAG
├── .env.example              # Environment variable template
└── README.md
```

---

---

## 🚀 Getting Started

The project has moved to a **Unified Cloud Backend**.

### [👉 Unified Quick Start Guide](../QUICKSTART.md)

Please refer to the root `QUICKSTART.md` for both Mobile and Azure Cloud setup. Localhost development is no longer the primary method for this project stage.

---

## 🛠️ How It Works

```
User Message
    │
    ▼
┌──────────────┐     ┌──────────────────────┐
│   FastAPI     │────▶│   Azure AI Agent     │
│   /chat       │     │   (Foundry)          │
└──────────────┘     └──────┬───────────────┘
                            │
                   Agent decides: tool call?
                            │
                ┌───────────┼───────────────┐
                ▼           ▼               ▼
         check_leave   book_room      create_ticket
         (tools.py)    (tools.py)     (tools.py)
                │           │               │
                ▼           ▼               ▼
         leave_manager  room_manager  ticket_manager
         (mock JSON)    (mock JSON)   (mock JSON)
                │           │               │
                └───────────┼───────────────┘
                            ▼
                   Agent generates
                   friendly response
                            │
                            ▼
                        User sees
                        chat reply
```

The Azure AI Agent **automatically decides** whether to call a tool based on the user's message. The SDK handles the full lifecycle — no manual intent matching needed.

---

## 🧪 Testing

### Quick Smoke Test

With the server running, open another terminal:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What is my leave balance?\", \"user_id\": \"emp_001\"}"
```

### Test via Web UI

Visit [http://localhost:8000](http://localhost:8000) and try:
- *"What's my leave balance?"*
- *"Book Conference Room A for tomorrow at 2pm"*
- *"Create an IT ticket for a network issue"*
- *"Apply for 2 days annual leave starting next Monday"*

---

## 🤝 Contributing

1. **Fork** the repo
2. **Create a branch** — `git checkout -b feature/your-feature`
3. **Commit changes** — `git commit -m "Add your feature"`
4. **Push** — `git push origin feature/your-feature`
5. **Open a Pull Request**

### Adding a New Tool

To add a new employee management capability:

1. **Create a manager module** in `app/modules/` (e.g. `shuttle_manager.py`)
2. **Add a tool function** in `app/tools.py` with a detailed docstring (the SDK reads it to generate the schema)
3. **Register the function** in the `FunctionTool(functions=[...])` list at the bottom of `tools.py`
4. That's it — the agent will automatically know when to call your new tool!

---

## 📄 License

This project is for the **Chin Hin Hackathon — Business Challenge 5**.
