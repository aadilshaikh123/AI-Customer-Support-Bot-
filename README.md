# AI Customer Support Bot

An intelligent customer support chatbot with contextual memory, FAQ retrieval, and smart escalation capabilities.

## 🏗️ Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: Supabase (PostgreSQL + pgvector)
- **LLM**: Groq API (Llama 3.3 70B Versatile)
- **Frontend**: Gradio
- **ORM**: SQLAlchemy 2.0

## 🚀 Features

- ✅ AI-powered conversational responses
- ✅ Contextual memory (remembers conversation history)
- ✅ Semantic FAQ search
- ✅ Intelligent escalation detection
- ✅ Session tracking and persistence
- ✅ RESTful API with auto-generated docs
- ✅ Clean chat interface

## 🏛️ Architecture

```
┌─────────────┐      HTTP/REST     ┌──────────────┐
│   Gradio    │ ───────────────────▶│   FastAPI    │
│  Frontend   │                     │   Backend    │
│ (Port 7860) │◀─────────────────── │ (Port 8000)  │
└─────────────┘                     └──────────────┘
                                           │
                                           │ SQLAlchemy
                                           ▼
                    ┌──────────────────────────────────┐
                    │        Supabase PostgreSQL       │
                    │  ┌────────┬────────┬──────────┐  │
                    │  │Sessions│Messages│   FAQs   │  │
                    │  └────────┴────────┴──────────┘  │
                    └──────────────────────────────────┘
                                           
                    ┌──────────────────────────────────┐
                    │          Groq API                │
                    │  (Llama 3.3 70B Versatile)       │
                    └──────────────────────────────────┘
```

### Request Flow
1. User sends message via Gradio
2. Frontend calls `/api/chat` endpoint
3. Backend retrieves conversation history from DB
4. Semantic search finds relevant FAQs
5. Builds context prompt with history + FAQs
6. Calls Groq API for response
7. Checks escalation triggers
8. Saves message to DB
9. Returns response to user

## 📁 Project Structure

```
csupportbot/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py            # App entry point
│   │   ├── config.py          # Settings
│   │   ├── database.py        # DB connection
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # Business logic
│   │   └── utils/             # Prompts & helpers
│   ├── requirements.txt
│   └── setup_db.py
├── frontend/                   # Gradio interface
│   ├── app.py
│   └── requirements.txt
├── data/
│   └── faqs.json              # Sample FAQs
├── test_chatbot.py
├── QUICKSTART.md
└── PROJECT_SUMMARY.md
```

## 🔧 Setup Instructions

### Prerequisites

- Python 3.11+
- Supabase account (free tier)
- Groq API key (free at https://console.groq.com)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd csupportbot
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. **Install dependencies**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
pip install -r requirements.txt
```

4. **Initialize database**
```bash
cd backend
python setup_db.py
```

5. **Run the application**

```bash
# Terminal 1 - Backend
cd backend
python -m app.main

# Terminal 2 - Frontend (open new terminal)
cd frontend
python app.py
```

6. **Access the application**
- Frontend UI: http://localhost:7860
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📚 API Endpoints

### Chat
- `POST /api/chat` - Send a message and get AI response
- `POST /api/sessions` - Create new chat session
- `GET /api/sessions/{id}` - Get session history

### FAQs
- `GET /api/faqs` - List all FAQs
- `POST /api/faqs` - Add new FAQ (admin)

### Escalations
- `GET /api/escalations` - View escalated queries

## 🤖 LLM Prompts Used

### System Prompt
```
You are a helpful customer support assistant. Your role is to:
1. Answer customer questions clearly and professionally
2. Use the provided FAQ knowledge base when applicable
3. Maintain context from previous messages in the conversation
4. Be honest when you don't know something
5. Stay on topic and relevant to customer support

If you cannot answer a question confidently, say so and the query will be escalated to a human agent.
```

### Context Building
- Retrieves last 10 messages from conversation history
- Fetches top 3 relevant FAQs using semantic similarity
- Combines into structured prompt with conversation context

### Escalation Detection
The bot escalates when:
- Confidence score < 0.7
- Customer uses keywords: "human", "agent", "manager", "speak to someone"
- Same question asked 3+ times
- Response contains: "I don't know", "I'm not sure"

## 🎯 Evaluation Criteria Coverage

| Criteria | Implementation |
|----------|---------------|
| Conversational Accuracy | Groq LLM + semantic FAQ matching |
| Session Management | PostgreSQL sessions + message history |
| LLM Integration Depth | Context windows, prompt engineering, confidence scoring |
| Code Structure | Modular architecture with services, routers, models |

## 🧪 Testing

```bash
# Run tests
cd backend
pytest

# Test API manually
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1, "message": "How do I reset my password?"}'
```

## 🎬 Demo Video

[Link to demo video showcasing:]
- FAQ handling
- Contextual conversation
- Escalation scenario
- UI walkthrough

## 📝 License

MIT

## 👥 Author

[Your Name]
