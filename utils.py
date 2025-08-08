"""
Utility functions for text processing, chunking, and tokenization.
"""
import re
from typing import List, Dict, Any
import tiktoken

def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing extra whitespace and special characters.
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}]', '', text)
    return text.strip()

def split_text_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into chunks of approximately chunk_size tokens with overlap.
    
    Args:
        text: Input text to split
        chunk_size: Target number of tokens per chunk
        overlap: Number of tokens to overlap between chunks
    
    Returns:
        List of text chunks
    """
    # Clean the text first
    text = clean_text(text)
    
    # Initialize tokenizer
    encoding = tiktoken.get_encoding("cl100k_base")  # OpenAI's encoding
    
    # Tokenize the text
    tokens = encoding.encode(text)
    
    chunks = []
    start = 0
    
    while start < len(tokens):
        # Calculate end position for this chunk
        end = start + chunk_size
        
        # Decode tokens back to text
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        
        # Clean the chunk text
        chunk_text = clean_text(chunk_text)
        
        if chunk_text.strip():
            chunks.append(chunk_text)
        
        # Move start position for next chunk (with overlap)
        start = end - overlap
        
        # If we're near the end, break
        if start >= len(tokens):
            break
    
    return chunks

def extract_clauses(text: str) -> List[Dict[str, Any]]:
    """
    Extract legal clauses from text with their positions.
    
    Args:
        text: Input text
    
    Returns:
        List of dictionaries with clause text and metadata
    """
    clauses = []
    
    # Pattern to match clause-like structures
    clause_patterns = [
        r'(?:Clause|Section|Article)\s+\d+[\.:]?\s*[A-Z][^.]*\.',
        r'\d+\.\s*[A-Z][^.]*\.',
        r'[A-Z][^.]*\.',
    ]
    
    for pattern in clause_patterns:
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
        for match in matches:
            clause_text = match.group().strip()
            if len(clause_text) > 10:  # Filter out very short matches
                clauses.append({
                    'text': clause_text,
                    'start': match.start(),
                    'end': match.end(),
                    'pattern': pattern
                })
    
    return clauses

def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a text string.
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def format_response(answer: str, source_clause: str, reasoning: str) -> dict:
    """
    Format response with enhanced validation for competition quality.
    
    Args:
        answer: The main answer
        source_clause: Supporting clause from document
        reasoning: Legal/insurance reasoning
        
    Returns:
        Formatted response dictionary
    """
    # Validate and clean inputs
    if not answer or answer.strip() == "":
        answer = "Unable to determine answer from the provided document."
    
    if not source_clause or source_clause.strip() == "":
        source_clause = "No specific clause identified in the document."
    
    if not reasoning or reasoning.strip() == "":
        reasoning = "Based on analysis of the provided document content."
    
    # Ensure proper formatting
    formatted_response = {
        "answer": answer.strip(),
        "source_clause": source_clause.strip(),
        "reasoning": reasoning.strip()
    }
    
    # Quality checks
    if len(formatted_response["answer"]) < 10:
        formatted_response["answer"] = "The information is not available in the provided document."
    
    if "not available" in formatted_response["answer"].lower() or "unable to" in formatted_response["answer"].lower():
        formatted_response["source_clause"] = "No relevant clause found in the document."
        formatted_response["reasoning"] = "The requested information is not explicitly stated in the provided document."
    
    return formatted_response 