# Quick Start Guide

## Setup (5 minutes)

### 1. Install Python Dependencies

```powershell
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
pip install -r requirements.txt
```

### 2. Configure Environment

```powershell
# Copy example env file
cp .env.example .env

# Edit .env with your credentials:
# - DATABASE_URL from Supabase
# - GROQ_API_KEY from console.groq.com
```

### 3. Initialize Database

```powershell
cd backend
python setup_db.py
```

### 4. Run the Application

```powershell
# Terminal 1 - Backend
cd backend
python -m app.main

# Terminal 2 - Frontend (open new terminal)
cd frontend
python app.py
```

### 5. Access the App

- Frontend: http://localhost:7860
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Testing the Bot

Try these queries:
1. "How do I reset my password?" (FAQ match)
2. "What are your business hours?" (FAQ match)
3. "I have a custom enterprise question" (Should escalate)
4. "I want to speak to a human" (Triggers escalation)

---

## Getting API Keys

### Supabase
1. Go to https://supabase.com
2. Create new project (free)
3. Go to Settings > Database > Connection String
4. Select "Session mode" (Connection Pooling)
5. Copy the URI and paste into .env as DATABASE_URL

### Groq
1. Go to https://console.groq.com
2. Sign up (free)
3. Create API key
4. Copy to .env file

---

## Troubleshooting

**"Cannot connect to database"**
- Check DATABASE_URL in .env
- Ensure Supabase project is active

**"Groq API error"**
- Verify GROQ_API_KEY is correct
- Check you haven't exceeded free tier limits

**"Frontend can't reach backend"**
- Ensure backend is running on port 8000
- Check CORS_ORIGINS in backend/.env

---

## Next Steps

- Customize FAQs in `data/faqs.json`
- Adjust prompts in `backend/app/utils/prompts.py`
- Modify UI in `frontend/app.py`
- Deploy to Railway/Render for production
