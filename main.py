"""
FastAPI application for HackRx 6.0 - Bajaj Finserv
Main application file with the /hackrx/run endpoint
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
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