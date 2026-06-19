# 🚀 Quick Deployment Guide - MediVoice AI

## ✅ Deployment Complete!

Your AI Healthcare Chatbot is now deployed and running.

---

## 🌐 Access Your Application

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Main application interface |
| **Backend API** | http://localhost:8000 | REST API endpoints |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |

---

## 🎮 Quick Commands

### Start Application
```powershell
.\start.ps1
```

### Stop Application
- Press `Ctrl+C` in each terminal window

### Restart Application
```powershell
# Close all terminals, then:
.\start.ps1
```

---

## 📋 What's Running

### ✅ Backend (Port 8000)
- FastAPI Python application
- Google Gemini AI integration
- ML-based symptom triage
- JWT authentication
- SQLite database

### ✅ Frontend (Port 5173)
- React + TypeScript application
- Modern responsive UI
- Real-time chat interface
- Voice message support

### ⚠️ Redis (Not Installed)
- Optional caching layer
- Install for better performance:
  ```powershell
  choco install redis-64
  ```

---

## 🔑 Features Available Now

1. ✅ **User Registration & Login**
   - Email/password authentication
   - Google OAuth 2.0

2. ✅ **AI Medical Chat**
   - Powered by Google Gemini
   - Context-aware conversations

3. ✅ **Symptom Triage**
   - ML department recommendations
   - Confidence scoring

4. ✅ **Voice Messages**
   - Text-to-speech support
   - Audio playback

5. ✅ **User Profiles**
   - Medical history tracking
   - Session persistence

---

## 📖 Documentation Files

| File | Description |
|------|-------------|
| `DEPLOYMENT_GUIDE.md` | Complete deployment instructions for all platforms |
| `DEPLOYMENT_STATUS.md` | Current deployment status and configuration |
| `README_DEPLOYMENT.md` | This quick reference guide |
| `.env` | Environment configuration (API keys, settings) |

---

## 🔧 Configuration

Edit `.env` file to customize:

```env
# API Keys
GEMINI_API_KEY=your-key-here
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-secret

# Application Settings
APP_NAME=MediVoice AI
DEBUG=true
FRONTEND_URL=http://localhost:5173

# Database
DATABASE_URL=sqlite:///./healthcare.db

# Security
JWT_SECRET=your-secure-secret-key
```

---

## 🐛 Quick Troubleshooting

### Backend not responding?
```powershell
# Check if running
netstat -ano | findstr :8000

# Restart backend terminal
```

### Frontend not loading?
```powershell
# Check if running
netstat -ano | findstr :5173

# Clear browser cache
# Hard refresh: Ctrl+Shift+R
```

### Connection refused errors?
1. Ensure both backend and frontend are running
2. Check terminal windows for error messages
3. Verify ports 8000 and 5173 are not blocked by firewall

---

## 📈 Next Steps

### 1. Test the Application
- Open http://localhost:5173
- Create a user account
- Try chatting with the AI
- Test symptom triage feature

### 2. Add Advanced Features (Optional)
The spec includes 164 enhancement tasks for:
- Multi-language voice support
- Emergency detection
- MFA authentication
- HIPAA compliance
- Dark mode
- Accessibility features
- Performance optimization

To implement these, tell Kiro:
```
"run all tasks for comprehensive-chatbot-enhancements spec"
```

### 3. Production Deployment (Optional)
See `DEPLOYMENT_GUIDE.md` for:
- Docker deployment
- Cloud platform deployment (AWS, GCP, Azure)
- VPS deployment
- SSL certificate setup
- Database migration to PostgreSQL

---

## 🎯 Common Tasks

### View Backend Logs
Check the terminal running `uvicorn`

### View Frontend Logs
Check the terminal running `npm run dev`

### Access Database
```powershell
# Using Python
python
>>> from backend.app.database.connection import get_db
>>> db = next(get_db())
```

### Update Dependencies
```powershell
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Production Build
```powershell
# Frontend production build
cd frontend
npm run build

# Preview production build
npm run preview
```

---

## 📞 Getting Help

1. **Check Logs**: Look at terminal output for errors
2. **Review Docs**: See `DEPLOYMENT_GUIDE.md` for details
3. **API Docs**: Visit http://localhost:8000/docs for API reference
4. **Environment**: Verify `.env` has all required values

---

## 🎉 Success Checklist

- [x] Python 3.13.5 installed
- [x] Node.js v22.20.0 installed
- [x] Dependencies installed
- [x] ML model trained
- [x] Backend running on port 8000
- [x] Frontend running on port 5173
- [x] Application accessible in browser
- [ ] Redis installed (optional but recommended)
- [ ] Production deployment (when ready)

---

## 💡 Pro Tips

1. **Development Mode**: Auto-reloads on code changes
2. **API Testing**: Use http://localhost:8000/docs to test endpoints
3. **Database Viewer**: Use DB Browser for SQLite to view database
4. **Multiple Terminals**: Keep backend and frontend in separate windows
5. **Browser DevTools**: F12 to see network requests and console logs

---

## 🔐 Security Reminder

For production deployment:
- [ ] Change `JWT_SECRET` to new random value
- [ ] Set `DEBUG=false`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS with SSL certificate
- [ ] Install and configure Redis
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure CORS for your domain only

---

**Your MediVoice AI Healthcare Chatbot is ready to use! 🎊**

Open http://localhost:5173 in your browser to get started.
