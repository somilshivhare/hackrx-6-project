# 🚀 HackRx 6.0 - Document Q&A API

A FastAPI-based AI system that answers questions from PDF documents using Google Gemini, TF-IDF embeddings, and FAISS vector search for the HackRx 6.0 competition.

## 🎯 Project Overview

This project implements a complete document question-answering system for HackRx 6.0 (Bajaj Finserv) that:

* ✅ Accepts user questions and PDF document URLs
* ✅ Uses Google Gemini + TF-IDF + FAISS for intelligent answers
* ✅ Returns structured JSON with source clauses and reasoning
* ✅ Uses only approved tools (no LangChain, Haystack, etc.)
* ✅ Provides clear step-by-step setup instructions
* ✅ Optimized for cost-effectiveness and reliability
* ✅ Ready for deployment on Render/Railway/Fly.io

## 🏗️ Architecture

```
hackrx_project/
├── main.py                    # FastAPI application with /hackrx/run endpoint
├── document_parser.py         # PDF downloading and text extraction
├── embedder_simple.py         # TF-IDF embeddings + FAISS vector search
├── llm_answerer_gemini.py    # Google Gemini prompting and answer generation
├── utils.py                  # Text chunking, tokenization, utilities
├── requirements.txt          # Python dependencies
├── render.yaml              # Render deployment configuration
├── .env                     # Environment variables (create this)
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## 🚀 Quick Start

### Step 1: Environment Setup

1. **Clone the repository:**
```bash
git clone https://github.com/somilshivhare/hackrx_project.git
cd hackrx_project
```

2. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Keys

1. **Create .env file:**
```bash
cp env_template.txt .env
```

2. **Edit .env file with your Google Gemini API key:**
```
GOOGLE_API_KEY=your-google-gemini-api-key-here
```

**Get your Google Gemini API key:**
- Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
- Sign in with your Google account
- Click "Create API Key"
- Copy the API key (starts with `AIza...`)

### Step 3: Run the Application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://127.0.0.1:8000`

### Step 4: Test the API

**Health Check:**
```bash
curl http://127.0.0.1:8000/
```

**Main Endpoint:**
```bash
curl -X POST http://127.0.0.1:8000/hackrx/run \
-H "Authorization: Bearer c3d64f143a0f199ddaa8e69856eaaeffa4d101bf633c771f581e441ba15ae106" \
-H "Content-Type: application/json" \
-d '{
  "documents": "https://example.com/sample.pdf",
  "questions": [
    "What is the grace period for premium payment?",
    "Does this policy cover maternity expenses?"
  ]
}'
```

## 📋 API Endpoints

### POST `/hackrx/run`

**Request Body:**
```json
{
  "documents": "https://example.com/document.pdf",
  "questions": [
    "Question 1",
    "Question 2",
    "Question 3"
  ]
}
```

**Response:**
```json
{
  "answers": [
    {
      "answer": "Yes, covered after 2 years.",
      "source_clause": "Clause 4.3: Cataract is covered after 24 months.",
      "reasoning": "Clause 4.3 matches question and confirms delay."
    },
    {
      "answer": "No, maternity expenses are excluded.",
      "source_clause": "Section 2.1: Maternity and pregnancy-related expenses are not covered.",
      "reasoning": "Section 2.1 explicitly excludes maternity coverage."
    }
  ]
}
```

### GET `/health`

Health check endpoint for deployment monitoring.

## 🔧 Technical Details

### Core Components

1. **Document Parser (`document_parser.py`)**
   * Downloads PDFs from URLs
   * Extracts text using PDFPlumber
   * Handles text cleaning and normalization

2. **Embedder (`embedder_simple.py`)**
   * Splits text into ~500 token chunks
   * Generates TF-IDF embeddings using scikit-learn
   * Creates FAISS index for similarity search
   * Retrieves top-k relevant chunks

3. **LLM Answerer (`llm_answerer_gemini.py`)**
   * Uses Google Gemini for answer generation
   * Implements structured prompting
   * Extracts source clauses and reasoning
   * Validates answer quality

4. **Utils (`utils.py`)**
   * Text chunking with overlap
   * Token counting using tiktoken
   * Clause extraction
   * Response formatting

### Key Features

* **No Hallucination**: Only uses retrieved document chunks
* **Source Attribution**: Always quotes exact clauses
* **Legal Focus**: Optimized for legal document analysis
* **Structured Output**: Consistent JSON response format
* **Error Handling**: Graceful fallbacks and validation
* **Cost Effective**: Uses local TF-IDF instead of expensive embeddings
* **Reliable**: Google Gemini API with better uptime

## 🌐 Deployment for HackRx

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
   - Connect your GitHub repo
   - Create new Web Service
   - Set environment variables:
     - `GOOGLE_API_KEY`: Your Google Gemini API key
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Get Public URL:**
   Your API will be available at: `https://your-app-name.onrender.com/hackrx/run`

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

## 🧪 Testing

### Local Testing

```bash
# Test with sample PDF
curl -X POST http://127.0.0.1:8000/hackrx/run \
-H "Authorization: Bearer c3d64f143a0f199ddaa8e69856eaaeffa4d101bf633c771f581e441ba15ae106" \
-H "Content-Type: application/json" \
-d '{
  "documents": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
  "questions": ["What is this document about?"]
}'
```

### Deployment Testing

```bash
# Test your deployed API
python test_deployment.py
```

## 🔍 Troubleshooting

### Common Issues

1. **Google Gemini API Key Error:**
   * Ensure `.env` file exists with correct API key
   * Check API key validity in Google AI Studio

2. **PDF Download Issues:**
   * Verify PDF URL is accessible
   * Check if URL requires authentication

3. **Memory Issues:**
   * Large PDFs may cause memory problems
   * Consider chunking documents

4. **Rate Limiting:**
   * Google Gemini API has rate limits
   * Implement retry logic for production

### Debug Mode

Enable debug logging:

```bash
export PYTHONPATH=.
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
uvicorn main:app --reload --log-level debug
```

## 📊 Performance Optimization

### For Production

1. **Caching:**
   * Cache FAISS indices for repeated documents
   * Implement Redis for session management

2. **Async Processing:**
   * Use background tasks for large documents
   * Implement queue system for multiple requests

3. **Monitoring:**
   * Add Prometheus metrics
   * Implement request/response logging

## 🏆 HackRx Submission Checklist

* ✅ API deployed and accessible via HTTPS
* ✅ `/hackrx/run` endpoint working
* ✅ Returns proper JSON format
* ✅ Handles multiple questions
* ✅ Includes source clauses and reasoning
* ✅ No external dependencies beyond approved tools
* ✅ Error handling implemented
* ✅ Documentation complete
* ✅ Uses Google Gemini for reliability
* ✅ Uses TF-IDF for cost-effectiveness

## 📝 Submission Instructions

1. **Deploy your API** to Render/Railway/Fly.io
2. **Get your public URL** (e.g., `https://your-app.onrender.com/hackrx/run`)
3. **Go to HackRx Dashboard**: https://dashboard.hackrx.in/submissions
4. **Submit your webhook URL** with the endpoint
5. **Add notes**: "FastAPI + Google Gemini + TF-IDF + FAISS + PDFPlumber"
6. **Test with sample documents** provided by HackRx

## 📝 License

This project is created for HackRx 6.0 competition.

## 🤝 Support

For issues or questions:

1. Check the troubleshooting section
2. Review the code comments
3. Test with sample PDFs first

---

**Good luck with HackRx 6.0! 🚀** 