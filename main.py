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

# Demo HTML endpoints removed: API-only mode

@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """Lightweight demo UI to test the API for sharing in posts."""
    return """
<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>HackRx 6.0 - Document Q&A Demo</title>
  <meta name=\"description\" content=\"AI-powered PDF question answering demo (FastAPI + Gemini + TF-IDF)\" />
  <meta property=\"og:title\" content=\"HackRx 6.0 - Document Q&A Demo\" />
  <meta property=\"og:description\" content=\"Try the live PDF Q&A demo. Paste a PDF URL, ask questions, see cited answers.\" />
  <style>
    :root{--bg:#0f1226;--card:#15193a;--text:#e8e8f0;--muted:#aab;--accent:#7c5cfa;--ok:#2ecc71;--err:#ff5c5c}
    *{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:linear-gradient(135deg,#0f1226,#1a1f4a);color:var(--text)}
    .wrap{max-width:880px;margin:0 auto;padding:28px}
    .hero{padding:22px 18px 10px;text-align:center}
    .hero h1{margin:0 0 8px;font-size:28px}
    .hero p{margin:0;color:var(--muted)}
    .card{background:var(--card);border:1px solid #23284f;border-radius:14px;box-shadow:0 8px 28px rgba(0,0,0,.25);padding:18px;margin:18px 0}
    label{font-weight:600;display:block;margin:10px 0 6px}
    input,textarea{width:100%;background:#0f1330;color:var(--text);border:1px solid #2a2f60;border-radius:10px;padding:12px 14px}
    textarea{min-height:110px;resize:vertical}
    .row{display:grid;gap:14px;grid-template-columns:1fr}
    .btn{background:var(--accent);color:#fff;border:none;border-radius:10px;padding:12px 16px;font-weight:700;cursor:pointer;width:100%}
    .btn:disabled{opacity:.6;cursor:not-allowed}
    .muted{color:var(--muted)}
    .result{background:#0f1330;border-left:4px solid var(--ok);padding:14px;border-radius:10px;margin:12px 0}
    .result h3{margin:0 0 6px}
    .error{border-left-color:var(--err)}
    .flex{display:flex;gap:10px;align-items:center}
    .badge{background:#0c1030;border:1px solid #2a2f60;color:var(--muted);padding:6px 10px;border-radius:999px;font-size:12px}
    .footer{padding:12px;text-align:center;color:var(--muted)}
    code{background:#10143a;padding:2px 6px;border-radius:6px}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"hero\">
      <h1>🚀 HackRx 6.0 — Document Q&A</h1>
      <p class=\"muted\">FastAPI + Google Gemini + TF‑IDF · Live demo for LinkedIn</p>
    </div>

    <div class=\"card\">
      <div class=\"row\">
        <div>
          <label for=\"pdfUrl\">PDF Document URL</label>
          <input id=\"pdfUrl\" type=\"url\" placeholder=\"https://example.com/document.pdf\" value=\"https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf\" />
        </div>
        <div>
          <label for=\"questions\">Your Questions (one per line)</label>
          <textarea id=\"questions\">What is this document about?
What type of document is this?
What information does it contain?</textarea>
        </div>
        <button id=\"goBtn\" class=\"btn\">🔍 Analyze Document</button>
        <div class=\"flex\"><span class=\"badge\">Endpoint</span><code>/hackrx/run</code></div>
        <div id=\"status\" class=\"muted\"></div>
        <div id=\"out\"></div>
      </div>
    </div>

    <div class=\"footer\">Built by Somil Shivhare · Share this demo link in your post: <code>/demo</code></div>
  </div>

  <script>
    const qs = (s)=>document.querySelector(s);
    const btn = qs('#goBtn');
    const out = qs('#out');
    const statusEl = qs('#status');

    async function run(){
      const pdfUrl = qs('#pdfUrl').value.trim();
      const questions = qs('#questions').value.split('\n').map(x=>x.trim()).filter(Boolean);
      if(!pdfUrl || !questions.length){ alert('Provide PDF URL and at least one question'); return; }
      btn.disabled = true; statusEl.textContent = 'Processing… this may take a few seconds'; out.innerHTML = '';
      try{
        const r = await fetch('/hackrx/run', {
          method:'POST',
          headers:{ 'Authorization':'Bearer c3d64f143a0f199ddaa8e69856eaaeffa4d101bf633c771f581e441ba15ae106', 'Content-Type':'application/json' },
          body: JSON.stringify({ documents: pdfUrl, questions })
        });
        let data; try { data = await r.json(); } catch(parseErr){
          out.innerHTML = `<div class=\"result error\"><strong>❌ Response Parse Error:</strong> ${parseErr?.message||parseErr}</div>`; btn.disabled=false; return;
        }
        statusEl.textContent = '';
        if(r.ok && Array.isArray(data.answers)){
          let html = '<h3 class="muted">Results</h3>';
          data.answers.forEach((a,i)=>{
            html += `
              <div class=\"result\">
                <h3>❓ Question ${i+1}</h3>
                <div><strong>💬 Answer:</strong> ${a.answer||''}</div>
                <div><strong>📄 Source:</strong> ${a.source_clause||''}</div>
                <div><strong>🧠 Reasoning:</strong> ${a.reasoning||''}</div>
              </div>`;
          });
          out.innerHTML = html;
        } else {
          out.innerHTML = `<div class=\"result error\"><strong>❌ Error:</strong> ${data?.detail||'Failed to process document'}</div>`;
        }
      } catch(err){
        console.error(err);
        out.innerHTML = `<div class=\"result error\"><strong>❌ Network Error:</strong> ${err?.message||err}</div>`;
      } finally { btn.disabled = false; }
    }
    btn.addEventListener('click', run);
  </script>
</body>
</html>
    """

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