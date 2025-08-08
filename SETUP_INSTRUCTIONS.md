# 🚀 HackRx 6.0 - Quick Setup Guide

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Git (for deployment)

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

# Edit .env file and add your OpenAI API key:
# OPENAI_API_KEY=sk-your-actual-key-here
```

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
-H "Authorization: Bearer test-token" \
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
   git init
   git add .
   git commit -m "HackRx 6.0 submission"
   git remote add origin https://github.com/yourusername/hackrx-project.git
   git push -u origin main
   ```

2. **Deploy on Render:**
   - Go to [render.com](https://render.com)
   - Connect your GitHub repo
   - Create new Web Service
   - Set environment variable: `OPENAI_API_KEY`
   - Deploy!

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
   - Add notes: "FastAPI + GPT-4 + FAISS + PDFPlumber"

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

1. **"OpenAI API key not found"**
   - Check `.env` file exists and has correct key

2. **"Server not running"**
   - Run: `uvicorn main:app --reload`

3. **"PDF download failed"**
   - Check PDF URL is accessible
   - Try with sample PDF first

4. **"Import errors"**
   - Ensure virtual environment is activated
   - Run: `pip install -r requirements.txt`

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

---

**Total Setup Time: ~5 minutes** ⚡

**Good luck with HackRx 6.0! 🚀** 