# HackRx 6.0 - Document Q&A API

A FastAPI-based AI system that answers questions from PDF documents using GPT-4, FAISS vector search, and OpenAI embeddings.

## 🎯 Project Overview

This project implements a complete document question-answering system for HackRx 6.0 (Bajaj Finserv) that:

- ✅ Accepts user questions and PDF document URLs
- ✅ Uses FAISS + OpenAI + GPT-4 for intelligent answers
- ✅ Returns structured JSON with source clauses and reasoning
- ✅ Uses only approved tools (no LangChain, Haystack, etc.)
- ✅ Provides clear step-by-step setup instructions

## 🏗️ Architecture

```
hackrx_project/
├── main.py              # FastAPI application with /hackrx/run endpoint
├── document_parser.py   # PDF downloading and text extraction
├── embedder.py         # OpenAI embeddings + FAISS vector search
├── llm_answerer.py     # GPT-4 prompting and answer generation
├── utils.py            # Text chunking, tokenization, utilities
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
└── README.md          # This file
```

## 🚀 Quick Start

### Step 1: Environment Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Step 2: Configure API Keys

1. **Create .env file:**
   ```bash
   cp env_template.txt .env
   ```

2. **Edit .env file with your OpenAI API key:**
   ```ini
   OPENAI_API_KEY=sk-your-actual-openai-api-key-here
   ```

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
-H "Authorization: Bearer YOUR_TEAM_TOKEN" \
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
   - Downloads PDFs from URLs
   - Extracts text using PDFPlumber
   - Handles text cleaning and normalization

2. **Embedder (`embedder.py`)**
   - Splits text into ~500 token chunks
   - Generates embeddings using `text-embedding-3-large`
   - Creates FAISS index for similarity search
   - Retrieves top-k relevant chunks

3. **LLM Answerer (`llm_answerer.py`)**
   - Uses GPT-4 for answer generation
   - Implements structured prompting
   - Extracts source clauses and reasoning
   - Validates answer quality

4. **Utils (`utils.py`)**
   - Text chunking with overlap
   - Token counting using tiktoken
   - Clause extraction
   - Response formatting

### Key Features

- **No Hallucination**: Only uses retrieved document chunks
- **Source Attribution**: Always quotes exact clauses
- **Legal Focus**: Optimized for legal document analysis
- **Structured Output**: Consistent JSON response format
- **Error Handling**: Graceful fallbacks and validation

## 🌐 Deployment for HackRx

### Step 1: Choose Platform

Recommended platforms:
- **Render** (Free tier available)
- **Railway** (Simple deployment)
- **Fly.io** (Good performance)
- **Heroku** (Paid)

### Step 2: Deploy

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "HackRx 6.0 submission"
   git remote add origin https://github.com/yourusername/hackrx-project.git
   git push -u origin main
   ```

2. **Configure deployment:**
   - Set environment variables (OPENAI_API_KEY)
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 3: Get Public URL

Your API will be available at: `https://your-app-name.onrender.com/hackrx/run`

### Step 4: Submit to HackRx

1. Go to: https://dashboard.hackrx.in/submissions
2. Paste your webhook URL: `https://your-app-name.onrender.com/hackrx/run`
3. Add notes: "FastAPI + GPT-4 + FAISS + PDFPlumber"
4. Test with sample PDF and questions

## 🧪 Testing

### Local Testing

```bash
# Test with sample PDF
curl -X POST http://127.0.0.1:8000/hackrx/run \
-H "Authorization: Bearer test-token" \
-H "Content-Type: application/json" \
-d '{
  "documents": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
  "questions": ["What is this document about?"]
}'
```

### Sample PDF URLs for Testing

- W3C Dummy PDF: `https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf`
- Sample Insurance Policy: `https://example.com/sample-policy.pdf`

## 🔍 Troubleshooting

### Common Issues

1. **OpenAI API Key Error:**
   - Ensure `.env` file exists with correct API key
   - Check API key validity in OpenAI dashboard

2. **PDF Download Issues:**
   - Verify PDF URL is accessible
   - Check if URL requires authentication

3. **Memory Issues:**
   - Large PDFs may cause memory problems
   - Consider chunking documents

4. **Rate Limiting:**
   - OpenAI API has rate limits
   - Implement retry logic for production

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
   - Cache FAISS indices for repeated documents
   - Implement Redis for session management

2. **Async Processing:**
   - Use background tasks for large documents
   - Implement queue system for multiple requests

3. **Monitoring:**
   - Add Prometheus metrics
   - Implement request/response logging

## 🏆 HackRx Submission Checklist

- [ ] API deployed and accessible via HTTPS
- [ ] `/hackrx/run` endpoint working
- [ ] Returns proper JSON format
- [ ] Handles multiple questions
- [ ] Includes source clauses and reasoning
- [ ] No external dependencies beyond approved tools
- [ ] Error handling implemented
- [ ] Documentation complete

## 📝 License

This project is created for HackRx 6.0 competition.

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Test with sample PDFs first

---

**Good luck with HackRx 6.0! 🚀** 