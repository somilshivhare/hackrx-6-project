# 🚀 HackRx 6.0 - Complete Setup & Deployment Guide

## 📋 Prerequisites

- Python 3.8+
- Google Gemini API key
- Git (for deployment)
- GitHub account

## 🔧 Step-by-Step Setup

### 1. Environment Setup (2 minutes)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key (1 minute)

```bash
# Copy template
cp env_template.txt .env

# Edit .env file and add your Google Gemini API key:
# GOOGLE_API_KEY=your-google-gemini-api-key-here
```

**Get your Google Gemini API key:**
- Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
- Sign in with your Google account
- Click "Create API Key"
- Copy the API key (starts with `AIza...`)

### 3. Run Locally (1 minute)

```bash
uvicorn main:app --reload
```

API runs at: `http://127.0.0.1:8000`

### 4. Test the API (2 minutes)

```bash
# Test health check
curl http://127.0.0.1:8000/

# Test main endpoint
curl -X POST http://127.0.0.1:8000/hackrx/run \
-H "Authorization: Bearer c3d64f143a0f199ddaa8e69856eaaeffa4d101bf633c771f581e441ba15ae106" \
-H "Content-Type: application/json" \
-d '{
  "documents": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
  "questions": ["What is this document about?"]
}'
```

Or run the test script:
```bash
python test_api.py
```

## 🌐 Deploy to Production

### Option 1: Render (Recommended)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "HackRx 6.0 submission with Google Gemini"
   git push origin master
   ```

2. **Deploy on Render:**
   - Go to [render.com](https://render.com)
   - Create new workspace: `HackRx-6-Project`
   - Connect your GitHub repository
   - Create new Web Service
   - Configure:
     - **Name**: `hackrx-6-api`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Set environment variable: `GOOGLE_API_KEY`
   - Deploy!

3. **Get your public URL:**
   `https://your-app-name.onrender.com/hackrx/run`

### Option 2: Railway

1. **Deploy directly:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Deploy
   railway login
   railway init
   railway up
   ```

### Option 3: Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

## 📝 HackRx Submission

1. **Get your public URL** (e.g., `https://your-app.onrender.com/hackrx/run`)

2. **Submit to HackRx:**
   - Go to: https://dashboard.hackrx.in/submissions
   - Paste your webhook URL
   - Add notes: "FastAPI + Google Gemini + TF-IDF + FAISS + PDFPlumber"

## ✅ Verification Checklist

- [ ] API responds to health check
- [ ] `/hackrx/run` endpoint works
- [ ] Returns proper JSON format
- [ ] Handles multiple questions
- [ ] Includes source clauses
- [ ] Deployed with HTTPS
- [ ] Submitted to HackRx dashboard

## 🆘 Troubleshooting

**Common Issues:**

1. **"Google Gemini API key not found"**
   - Check `.env` file exists and has correct key
   - Verify API key starts with `AIza...`

2. **"Server not running"**
   - Run: `uvicorn main:app --reload`

3. **"PDF download failed"**
   - Check PDF URL is accessible
   - Try with sample PDF first

4. **"Import errors"**
   - Ensure virtual environment is activated
   - Run: `pip install -r requirements.txt`

5. **"Deployment failed"**
   - Check environment variables are set correctly
   - Verify build command: `pip install -r requirements.txt`
   - Verify start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## 🎯 Expected Response Format

```json
{
  "answers": [
    {
      "answer": "Yes, covered after 2 years.",
      "source_clause": "Clause 4.3: Cataract is covered after 24 months.",
      "reasoning": "Clause 4.3 matches question and confirms delay."
    }
  ]
}
```

## 🚀 Quick Deployment Commands

```bash
# 1. Setup local environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure API key
cp env_template.txt .env
# Edit .env and add your Google Gemini API key

# 3. Test locally
uvicorn main:app --reload

# 4. Deploy to Render
git add .
git commit -m "HackRx 6.0 submission"
git push origin master
# Then deploy on render.com

# 5. Submit to HackRx
# Go to dashboard.hackrx.in/submissions
# Submit your webhook URL
```

---

**Total Setup Time: ~5 minutes** ⚡

**Good luck with HackRx 6.0! 🚀** 