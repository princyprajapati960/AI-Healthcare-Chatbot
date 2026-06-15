# MediVoice AI — Multilingual Healthcare Triage Agent

Professional AI healthcare platform with Copilot-style chat, voice assistant, ML triage, and **same-language conversation continuity** (English, Hindi, Marathi, Gujarati).

## Features

- SEO-optimized landing page
- Email + Google OAuth authentication
- Patient onboarding (profile + language selection)
- ChatGPT-style chat with typing indicator
- TF-IDF + Logistic Regression department triage
- gTTS voice playback + browser speech recognition
- Same-language responses enforced via system prompt + leakage detection

## Prerequisites

- Python 3.11+
- Node.js 18+
- Chrome (recommended for voice input)

## Quick Start (Windows)

### 1. Backend

```powershell
cd "D:\Coding\AI healthcare"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python -m backend.train_model
uvicorn backend.app.main:app --reload --port 8000
```

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Description |
|----------|----------|-------------|
| `JWT_SECRET` | Yes | Random secret for JWT tokens |
| `OPENAI_API_KEY` | Optional | Enables smarter replies; fallback responses work without it |
| `GOOGLE_CLIENT_ID` | Optional | Google Sign-In |
| `GOOGLE_CLIENT_SECRET` | Optional | Google Sign-In |

## User Flow

1. **Landing page** → Sign up / Login / Google
2. **Onboarding** → Name, age, gender, address, phone, language
3. **Chat** → Personalized greeting in chosen language
4. **Voice** → Mic to speak, speaker to hear replies
5. **End session** → Farewell in chosen language

## Project Structure

```
ai-healthcare/
├── frontend/          React + Vite + Tailwind
├── backend/
│   ├── app/           FastAPI application
│   ├── data/          Triage training CSV
│   └── models/        Saved ML model
├── audio/             Generated TTS files
├── requirements.txt
└── README.md
```

## API Health Check

```powershell
curl http://localhost:8000/api/health
```

## Google OAuth Setup

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google+ API / OAuth consent screen
3. Create OAuth 2.0 credentials (Web application)
4. Authorized redirect URI: `http://localhost:8000/api/auth/google/callback`
5. Add `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` to `.env`

## Disclaimer

This platform provides AI guidance only. It is **not** a substitute for professional medical diagnosis or treatment.
