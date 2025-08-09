"""
Main document processing API endpoint - optimized for size
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import time
import asyncio

app = FastAPI()

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
        import sys
        sys.path.append('..')
        from document_parser import DocumentParser
        _document_parser = DocumentParser()
    return _document_parser

def get_embedder():
    """Lazy load embedder"""
    global _embedder
    if _embedder is None:
        import sys
        sys.path.append('..')
        from embedder_simple import SimpleEmbedder
        _embedder = SimpleEmbedder()
    return _embedder

def get_llm_answerer():
    """Lazy load LLM answerer"""
    global _llm_answerer
    if _llm_answerer is None:
        import sys
        sys.path.append('..')
        from llm_answerer_gemini import LLMAnswerer
        _llm_answerer = LLMAnswerer()
    return _llm_answerer

def get_format_response():
    """Lazy load utils"""
    import sys
    sys.path.append('..')
    from utils import format_response
    return format_response

async def verify_team_token(authorization: Optional[str] = Header(None)):
    """Verify team token for HackRx submission"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return authorization.replace("Bearer ", "")

@app.post("/hackrx/run", response_model=HackRxResponse)
async def run_hackrx(
    request: HackRxRequest,
    team_token: str = Depends(verify_team_token)
):
    """
    Ultra-optimized main endpoint for HackRx 6.0
    """
    start_time = time.time()
    
    try:
        # Step 1: Download and parse the PDF document
        print(f"📄 Processing document: {request.documents}")
        document_parser = get_document_parser()
        pdf_text = await document_parser.parse_pdf_from_url(str(request.documents))
        
        if not pdf_text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
        
        # Step 2: Create embeddings
        print("🔍 Creating embeddings...")
        embedder = get_embedder()
        faiss_index = await embedder.create_faiss_index(pdf_text)
        
        # Step 3: Process questions
        print(f"❓ Processing {len(request.questions)} questions...")
        answers = []
        
        for i, question in enumerate(request.questions):
            print(f"Processing question {i+1}: {question}")
            
            # Retrieve relevant chunks
            relevant_chunks = await embedder.search_similar_chunks(
                faiss_index, question, top_k=5
            )
            
            # Generate answer
            llm_answerer = get_llm_answerer()
            answer_data = await llm_answerer.generate_answer(
                question, relevant_chunks, pdf_text
            )
            
            # Format response
            format_response = get_format_response()
            formatted_answer = format_response(
                answer=answer_data["answer"],
                source_clause=answer_data["source_clause"],
                reasoning=answer_data["reasoning"]
            )
            
            answers.append(formatted_answer)
        
        total_time = time.time() - start_time
        print(f"✅ Completed in {total_time:.2f}s")
        
        return HackRxResponse(answers=answers)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
