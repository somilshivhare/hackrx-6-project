#!/usr/bin/env python3
"""
Debug script to test individual components
"""
import asyncio
import os
from dotenv import load_dotenv
from document_parser import DocumentParser
from embedder_simple import SimpleEmbedder as Embedder
from llm_answerer_gemini import LLMAnswerer

# Load environment variables
load_dotenv()

async def test_components():
    """Test each component separately"""
    print("🔍 Testing individual components...")
    
    # Test 1: Document Parser
    print("\n1️⃣ Testing Document Parser...")
    try:
        parser = DocumentParser()
        # Test with a simple text instead of PDF
        test_text = "This is a test document about insurance policies. The grace period is 30 days."
        print("✅ Document parser initialized successfully")
    except Exception as e:
        print(f"❌ Document parser failed: {e}")
        return
    
    # Test 2: Embedder
    print("\n2️⃣ Testing Embedder...")
    try:
        embedder = Embedder()
        print("✅ Embedder initialized successfully")
        
        # Test embedding generation
        test_chunks = ["This is a test chunk about insurance.", "Another test chunk about policies."]
        embeddings = await embedder._generate_embeddings(test_chunks)
        if embeddings:
            print(f"✅ Embeddings generated successfully: {len(embeddings)} vectors")
        else:
            print("❌ Failed to generate embeddings")
            return
    except Exception as e:
        print(f"❌ Embedder failed: {e}")
        return
    
    # Test 3: LLM Answerer
    print("\n3️⃣ Testing LLM Answerer...")
    try:
        llm = LLMAnswerer()
        print("✅ LLM Answerer initialized successfully")
    except Exception as e:
        print(f"❌ LLM Answerer failed: {e}")
        return
    
    print("\n✅ All components working correctly!")

if __name__ == "__main__":
    asyncio.run(test_components())
