# 🚀 Deploy to Vercel - Complete Guide

## 📋 Prerequisites

- GitHub account
- Google Gemini API key
- Vercel account (free)

## 🔧 Step-by-Step Deployment

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Login to Vercel

```bash
vercel login
```

### Step 3: Deploy from GitHub

1. **Go to [vercel.com](https://vercel.com)**
2. **Sign up/Login** with your GitHub account
3. **Click "New Project"**
4. **Import your repository**: `somilshivhare/hackrx-6-project`
5. **Configure settings**:
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave default)
   - **Build Command**: Leave empty (Vercel auto-detects)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

### Step 4: Set Environment Variables

1. **Go to your project dashboard**
2. **Click "Settings" → "Environment Variables"**
3. **Add variable**:
   - **Name**: `GOOGLE_API_KEY`
   - **Value**: Your Google Gemini API key
   - **Environment**: Production, Preview, Development

### Step 5: Deploy

1. **Click "Deploy"**
2. **Wait for deployment** (2-3 minutes)
3. **Get your URL**: `https://your-project.vercel.app`

## 🎯 Your API Endpoints

- **Health Check**: `https://your-project.vercel.app/`
- **Main API**: `https://your-project.vercel.app/hackrx/run`

## 🧪 Test Your Deployment

```bash
# Health check
curl https://your-project.vercel.app/

# Test main endpoint
curl -X POST https://your-project.vercel.app/hackrx/run \
-H "Authorization: Bearer c3d64f143a0f199ddaa8e69856eaaeffa4d101bf633c771f581e441ba15ae106" \
-H "Content-Type: application/json" \
-d '{
  "documents": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
  "questions": ["What is this document about?"]
}'
```

## 📝 Submit to HackRx

1. **Go to**: https://dashboard.hackrx.in/submissions
2. **Webhook URL**: `https://your-project.vercel.app/hackrx/run`
3. **Notes**: "FastAPI + Google Gemini + TF-IDF + Vercel"

## ✅ Advantages of Vercel

- **No build issues** - Handles Python dependencies better
- **Faster deployments** - 2-3 minutes vs 5-10 on Render
- **Automatic deployments** - Push to GitHub = auto-deploy
- **Better performance** - Global edge network
- **Easy environment variables** - Simple UI

## 🆘 Troubleshooting

### Common Issues:

1. **"Module not found"**
   - Check requirements.txt is in root directory
   - Ensure all dependencies are listed

2. **"Environment variable not found"**
   - Add GOOGLE_API_KEY in Vercel dashboard
   - Redeploy after adding variables

3. **"Function timeout"**
   - Increase timeout in vercel.json (maxDuration: 30)

## 🚀 Quick Deploy Commands

```bash
# Deploy from command line
vercel

# Deploy to production
vercel --prod

# Set environment variable
vercel env add GOOGLE_API_KEY
```

---

**Your API will be live at**: `https://your-project.vercel.app/hackrx/run`

**Good luck with HackRx 6.0! 🚀**
