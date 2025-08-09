"""
FastAPI application for HackRx 6.0 - Bajaj Finserv
Main application file with the /hackrx/run endpoint
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import time
import asyncio

# Lazy imports - only import when needed to reduce cold start bundle

app = FastAPI(
    title="HackRx 6.0 - Document Q&A API",
    description="AI-powered document question answering system using Google Gemini and TF-IDF",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class HackRxRequest(BaseModel):
    documents: str
    questions: List[str]

class HackRxResponse(BaseModel):
    answers: List[dict]

# Lazy loading globals
_document_parser = None
_embedder = None
_llm_answerer = None

def get_document_parser():
    """Lazy load document parser"""
    global _document_parser
    if _document_parser is None:
        from document_parser import DocumentParser
        _document_parser = DocumentParser()
    return _document_parser

def get_embedder():
    """Lazy load embedder"""
    global _embedder
    if _embedder is None:
        from embedder_simple import SimpleEmbedder
        _embedder = SimpleEmbedder()
    return _embedder

def get_llm_answerer():
    """Lazy load LLM answerer"""
    global _llm_answerer
    if _llm_answerer is None:
        from llm_answerer_gemini import LLMAnswerer
        _llm_answerer = LLMAnswerer()
    return _llm_answerer

def get_format_response():
    """Lazy load utils"""
    from utils import format_response
    return format_response

# Simple cache for document processing
document_cache = {}

async def verify_team_token(authorization: Optional[str] = Header(None)):
    """Verify team token for HackRx submission"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    # For HackRx, you can implement your own token verification logic
    # For now, we'll accept any Bearer token
    return authorization.replace("Bearer ", "")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "HackRx 6.0 - Document Q&A API",
        "status": "running",
        "endpoint": "/hackrx/run",
        "public": True,
        "auth_test": "API is accessible without authentication"
    }

@app.post("/hackrx/run", response_model=HackRxResponse)
async def run_hackrx(
    request: HackRxRequest,
    team_token: str = Depends(verify_team_token)
):
    """
    Optimized main endpoint for HackRx 6.0 with performance tracking
    
    Accepts a PDF document URL and list of questions,
    processes them through the AI pipeline, and returns
    structured answers with source clauses and reasoning.
    """
    start_time = time.time()
    performance_metrics = {
        "document_processing_time": 0,
        "embedding_time": 0,
        "question_processing_times": [],
        "total_time": 0
    }
    
    try:
        # Step 1: Download and parse the PDF document
        print(f"📄 Processing document: {request.documents}")
        doc_start = time.time()
        document_parser = get_document_parser()
        pdf_text = await document_parser.parse_pdf_from_url(str(request.documents))
        performance_metrics["document_processing_time"] = time.time() - doc_start
        
        if not pdf_text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Step 2: Create embeddings and store in FAISS
        print("🔍 Creating embeddings and FAISS index...")
        embed_start = time.time()
        embedder = get_embedder()
        faiss_index = await embedder.create_faiss_index(pdf_text)
        performance_metrics["embedding_time"] = time.time() - embed_start
        
        # Step 3: Process each question with timing
        print(f"❓ Processing {len(request.questions)} questions...")
        answers = []
        
        for i, question in enumerate(request.questions):
            question_start = time.time()
            print(f"Processing question {i+1}: {question}")
            
            # Retrieve relevant chunks from FAISS
            relevant_chunks = await embedder.search_similar_chunks(
                faiss_index, question, top_k=5
            )
            
            # Generate answer using Google Gemini with enhanced context
            llm_answerer = get_llm_answerer()
            answer_data = await llm_answerer.generate_answer(
                question, relevant_chunks, pdf_text
            )
            
            # Format response with enhanced quality validation
            format_response = get_format_response()
            formatted_answer = format_response(
                answer=answer_data["answer"],
                source_clause=answer_data["source_clause"],
                reasoning=answer_data["reasoning"]
            )
            
            # Validate answer quality before adding to results
            quality_check = llm_answerer.validate_answer_quality(answer_data)
            if not quality_check["is_acceptable"]:
                print(f"⚠️ Warning: Question {i+1} may have quality issues: {quality_check['issues']}")
            
            answers.append(formatted_answer)
            performance_metrics["question_processing_times"].append(time.time() - question_start)
        
        performance_metrics["total_time"] = time.time() - start_time
        
        print(f"✅ Successfully processed {len(answers)} questions")
        print(f"📊 Performance Metrics:")
        print(f"   - Document processing: {performance_metrics['document_processing_time']:.2f}s")
        print(f"   - Embedding creation: {performance_metrics['embedding_time']:.2f}s")
        print(f"   - Average question time: {sum(performance_metrics['question_processing_times'])/len(performance_metrics['question_processing_times']):.2f}s")
        print(f"   - Total processing time: {performance_metrics['total_time']:.2f}s")
        
        return HackRxResponse(answers=answers)
        
    except Exception as e:
        print(f"❌ Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/demo", response_class=HTMLResponse)
@app.get("/demo.html", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
async def demo_page():
    """Interactive demo page"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>HackRx 6.0 - Document Q&A Demo</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .header { text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }
        .demo-box { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .btn { background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .result { background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 15px; border-left: 4px solid #28a745; }
        input, textarea { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .tech-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .tech-item { background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 HackRx 6.0 - Document Q&A</h1>
        <p>AI-Powered Insurance Document Analysis by Somil Shivhare</p>
    </div>
    
    <div class="demo-box">
        <h2>📄 Live API Demo</h2>
        <p><strong>Status:</strong> <span style="color: green;">✅ API Live & Running</span></p>
        <p><strong>Endpoint:</strong> <code>https://hackrx-6-project-23a2.vercel.app/hackrx/run</code></p>
        
        <label>PDF Document URL:</label>
        <input type="text" id="pdfUrl" value="https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf" placeholder="Enter PDF URL here...">
        
        <label>Your Questions (one per line):</label>
        <textarea id="questions" rows="4" placeholder="What is this document about?&#10;What are the key terms?">What is this document about?
What type of document is this?
What information does it contain?</textarea>
        
        <button class="btn" onclick="testAPI()" style="width: 100%; margin-top: 10px;">🔍 Analyze Document with AI</button>
        
        <div id="result" style="display:none;"></div>
    </div>
    
    <div class="demo-box">
        <h2>🔧 Technical Architecture</h2>
        <div class="tech-grid">
            <div class="tech-item">
                <h3>🚀 FastAPI</h3>
                <p>High-performance REST API framework</p>
            </div>
            <div class="tech-item">
                <h3>🤖 Google Gemini</h3>
                <p>Advanced language model for intelligent responses</p>
            </div>
            <div class="tech-item">
                <h3>📊 TF-IDF</h3>
                <p>Custom text similarity search engine</p>
            </div>
            <div class="tech-item">
                <h3>☁️ Vercel</h3>
                <p>Serverless deployment platform</p>
            </div>
        </div>
    </div>

    <div class="demo-box">
        <h2>🎯 Features</h2>
        <ul>
            <li>✅ Process PDF documents from URLs</li>
            <li>✅ Intelligent Q&A with source citations</li>
            <li>✅ Built for insurance & legal analysis</li>
            <li>✅ Real-time document processing</li>
            <li>✅ Structured JSON responses</li>
            <li>✅ Optimized for performance (< 250MB)</li>
        </ul>
    </div>

    <script>
        async function testAPI() {
            const resultDiv = document.getElementById('result');
            const pdfUrl = document.getElementById('pdfUrl').value;
            const questions = document.getElementById('questions').value.split('\\n').filter(q => q.trim());
            
            if (!pdfUrl || questions.length === 0) {
                alert('Please provide both PDF URL and questions');
                return;
            }
            
            resultDiv.innerHTML = '<p style="text-align: center;">🔄 Processing document with AI... This may take 10-20 seconds.</p>';
            resultDiv.style.display = 'block';
            
            try {
                const response = await fetch('/hackrx/run', {
                    method: 'POST',
                    headers: {
                        'Authorization': 'Bearer c3d64f143a0f199ddaa8e69856eaaeffa4d101bf633c771f581e441ba15ae106',
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ documents: pdfUrl, questions: questions })
                });
                
                const data = await response.json();
                
                if (data.answers) {
                    let html = '<h3>✅ AI Analysis Results:</h3>';
                    data.answers.forEach((answer, i) => {
                        html += `<div class="result" style="margin-bottom: 15px;">
                            <strong>❓ Question ${i+1}:</strong> ${questions[i]}<br><br>
                            <strong>💬 Answer:</strong> ${answer.answer}<br><br>
                            <strong>📄 Source Clause:</strong> ${answer.source_clause}<br><br>
                            <strong>🧠 AI Reasoning:</strong> ${answer.reasoning}
                        </div>`;
                    });
                    resultDiv.innerHTML = html;
                } else {
                    resultDiv.innerHTML = `<div class="result" style="border-left-color: #dc3545;"><p>❌ <strong>Error:</strong> ${data.detail || 'Unknown error occurred'}</p><p>Try with a different PDF URL or check if the document is accessible.</p></div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<div class="result" style="border-left-color: #dc3545;"><p>❌ <strong>Network Error:</strong> ${error.message}</p></div>`;
            }
        }
    </script>

    <div style="text-align: center; margin-top: 30px; color: #666;">
        <p>Built for <strong>HackRx 6.0</strong> by <strong>Bajaj Finserv</strong></p>
        <p>Created by Somil Shivhare | <a href="https://linkedin.com/in/somilshivhare" target="_blank">LinkedIn</a></p>
    </div>
</body>
</html>
    """
    return html_content

@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "healthy",
        "google_api_key_configured": bool(os.getenv("GOOGLE_API_KEY")),
        "service": "hackrx-document-qa",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 