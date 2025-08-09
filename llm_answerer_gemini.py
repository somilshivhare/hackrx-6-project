"""
LLM Answerer module using Google Gemini for generating answers from document chunks.
Handles prompting, context processing, and structured response generation.
"""
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio
from typing import List, Dict, Any, Optional
import os
import re

from utils import extract_clauses

# Load environment variables from a local .env file when present (for local/dev only)
load_dotenv()

class LLMAnswerer:
    """Handles Gemini-based answer generation from document chunks"""
    
    def __init__(self):
        # Initialize Gemini client (support alternate env var name used in Vercel)
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY2")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY/GOOGLE_API_KEY2 not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.max_tokens = 1000
        self.temperature = 0.1  # Low temperature for consistent legal answers
    
    async def generate_answer(
        self, 
        question: str, 
        relevant_chunks: List[str], 
        full_document: str
    ) -> Dict[str, str]:
        """
        Generate answer using Gemini based on relevant document chunks.
        
        Args:
            question: User's question
            relevant_chunks: Retrieved relevant text chunks
            full_document: Full document text for context
            
        Returns:
            Dictionary with answer, source_clause, and reasoning
        """
        try:
            # Prepare context from relevant chunks
            context = self._prepare_context(relevant_chunks)
            
            # Create prompt for Gemini
            prompt = self._create_prompt(question, context)
            
            # Generate response using Gemini
            print(f"🤖 Generating answer for: {question[:50]}...")
            response = await self._call_gemini(prompt)
            
            if not response:
                raise ValueError("Failed to generate response from Gemini")
            
            # Parse and structure the response
            structured_response = self._parse_response(response, relevant_chunks, full_document)
            
            return structured_response
            
        except Exception as e:
            print(f"❌ Error generating answer: {str(e)}")
            return self._create_fallback_response(question)
    
    def _prepare_context(self, chunks: List[str]) -> str:
        """Prepare context from relevant chunks"""
        if not chunks:
            return "No relevant information found in the document."
        
        # Combine chunks with clear separators
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"CHUNK {i}:\n{chunk}\n")
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, question: str, context: str) -> str:
        """Create optimized prompt for Gemini with enhanced accuracy"""
        return f"""You are an expert insurance and legal document analyst with deep expertise in policy interpretation. Your task is to provide precise, accurate answers based on the provided document context.

DOCUMENT CONTEXT:
{context}

QUESTION: {question}

CRITICAL INSTRUCTIONS:
1. Answer the question based ONLY on the provided document context
2. If the information is not explicitly stated in the context, respond with "The information is not available in the provided document"
3. Provide a clear, comprehensive answer that directly addresses the question
4. Quote the EXACT clause, section, or paragraph that supports your answer
5. Provide detailed legal/insurance reasoning for your conclusion
6. Include specific numbers, dates, percentages, and conditions mentioned in the document
7. If multiple conditions apply, list them all clearly

RESPONSE FORMAT:
Answer: [Your direct, comprehensive answer to the question]
Source Clause: [Exact quote from the document that supports your answer]
Reasoning: [Detailed legal/insurance justification based on the quoted clause]

ACCURACY REQUIREMENTS:
- Do not hallucinate or make assumptions beyond the provided context
- Only use information explicitly stated in the document
- Quote the exact text from the document with proper attribution
- Include section numbers, clause references, and page numbers if available
- Be precise with numbers, dates, and conditions
- If the answer involves multiple parts, address each part separately
- For coverage questions, clearly state what is covered and what is excluded
- For waiting periods, specify exact durations and conditions
- For limits and sub-limits, provide exact amounts and conditions

QUALITY STANDARDS:
- Ensure answers are legally accurate and professionally worded
- Maintain consistency with insurance industry terminology
- Provide complete information without omitting important details
- Structure complex answers in a clear, logical manner"""
    
    async def _call_gemini(self, prompt: str) -> Optional[str]:
        """Call Gemini API with retry logic and enhanced error handling"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(prompt)
                )
                
                return response.text.strip()
                
            except Exception as e:
                print(f"❌ Error calling Gemini (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print(f"❌ Failed to call Gemini after {max_retries} attempts")
                    return None
        
        return None
    
    def _parse_response(self, response: str, chunks: List[str], full_document: str) -> Dict[str, str]:
        """Parse Gemini response and extract structured components"""
        try:
            # Extract components using regex patterns
            answer_match = re.search(r'Answer:\s*(.+?)(?=\n|$)', response, re.IGNORECASE | re.DOTALL)
            source_match = re.search(r'Source Clause:\s*(.+?)(?=\n|$)', response, re.IGNORECASE | re.DOTALL)
            reasoning_match = re.search(r'Reasoning:\s*(.+?)(?=\n|$)', response, re.IGNORECASE | re.DOTALL)
            
            # Extract values
            answer = answer_match.group(1).strip() if answer_match else "Unable to determine answer from document."
            source_clause = source_match.group(1).strip() if source_match else "No specific clause identified."
            reasoning = reasoning_match.group(1).strip() if reasoning_match else "Based on document analysis."
            
            # Validate and improve source clause if needed
            if source_clause and source_clause != "No specific clause identified.":
                # Try to find the exact clause in the document
                exact_clause = self._find_exact_clause(source_clause, full_document)
                if exact_clause:
                    source_clause = exact_clause
            
            return {
                "answer": answer,
                "source_clause": source_clause,
                "reasoning": reasoning
            }
            
        except Exception as e:
            print(f"❌ Error parsing response: {str(e)}")
            return self._create_fallback_response("")
    
    def _find_exact_clause(self, quoted_text: str, full_document: str) -> Optional[str]:
        """Find exact clause in the document"""
        try:
            # Clean the quoted text
            clean_quote = re.sub(r'["\']', '', quoted_text).strip()
            
            # Look for exact match
            if clean_quote in full_document:
                return clean_quote
            
            # Look for partial matches
            words = clean_quote.split()
            if len(words) > 3:
                # Try to find a sequence of words
                for i in range(len(words) - 2):
                    phrase = " ".join(words[i:i+3])
                    if phrase in full_document:
                        # Expand to get more context
                        start_idx = full_document.find(phrase)
                        end_idx = start_idx + len(phrase)
                        
                        # Get surrounding context
                        context_start = max(0, start_idx - 100)
                        context_end = min(len(full_document), end_idx + 100)
                        
                        return full_document[context_start:context_end].strip()
            
            return None
            
        except Exception as e:
            print(f"❌ Error finding exact clause: {str(e)}")
            return None
    
    def _create_fallback_response(self, question: str) -> Dict[str, str]:
        """Create fallback response when processing fails"""
        return {
            "answer": "Unable to process the question due to technical issues. Please try again.",
            "source_clause": "No source clause available.",
            "reasoning": "Technical error prevented document analysis."
        }
    
    def validate_answer_quality(self, answer_data: Dict[str, str]) -> Dict[str, Any]:
        """Validate the quality of generated answer"""
        quality_score = 0
        issues = []
        
        # Check answer length
        if len(answer_data.get("answer", "")) < 10:
            issues.append("Answer too short")
            quality_score -= 1
        
        # Check source clause presence
        if not answer_data.get("source_clause") or answer_data["source_clause"] == "No specific clause identified.":
            issues.append("No source clause provided")
            quality_score -= 1
        
        # Check reasoning presence
        if not answer_data.get("reasoning") or len(answer_data.get("reasoning", "")) < 10:
            issues.append("Insufficient reasoning")
            quality_score -= 1
        
        # Check for hallucination indicators
        answer_text = answer_data.get("answer", "").lower()
        if any(phrase in answer_text for phrase in ["i don't know", "cannot determine", "not available", "unable to"]):
            quality_score += 1  # Honest about limitations
        
        return {
            "quality_score": quality_score,
            "issues": issues,
            "is_acceptable": quality_score >= -1
        }
