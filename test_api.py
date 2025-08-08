#!/usr/bin/env python3
"""
Test script for HackRx 6.0 API
Run this to test the API functionality locally
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get("http://127.0.0.1:8000/")
        print("✅ Health check passed")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_hackrx_endpoint():
    """Test the main HackRx endpoint"""
    url = "http://127.0.0.1:8000/hackrx/run"
    
    # Test payload
    payload = {
        "documents": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "questions": [
            "What is this document about?",
            "What is the purpose of this PDF?"
        ]
    }
    
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    
    try:
        print("🚀 Testing HackRx endpoint...")
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print("✅ HackRx endpoint test passed!")
            result = response.json()
            print(f"Number of answers: {len(result.get('answers', []))}")
            
            for i, answer in enumerate(result.get('answers', []), 1):
                print(f"\n--- Answer {i} ---")
                print(f"Answer: {answer.get('answer', 'N/A')}")
                print(f"Source: {answer.get('source_clause', 'N/A')}")
                print(f"Reasoning: {answer.get('reasoning', 'N/A')}")
            
            return True
        else:
            print(f"❌ HackRx endpoint test failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ HackRx endpoint test failed: {e}")
        return False

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Checking environment...")
    
    # Check Google Gemini API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key and api_key != "your-google-gemini-api-key-here":
        print("✅ Google Gemini API key configured")
    else:
        print("❌ Google Gemini API key not configured properly")
        print("Please set GOOGLE_API_KEY in your .env file")
        return False
    
    # Check if server is running
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print("✅ FastAPI server is running")
        return True
    except:
        print("❌ FastAPI server is not running")
        print("Please start the server with: uvicorn main:app --reload")
        return False

def main():
    """Main test function"""
    print("🧪 HackRx 6.0 API Test Suite")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        return
    
    print("\n" + "=" * 40)
    
    # Test health check
    if not test_health_check():
        return
    
    print("\n" + "=" * 40)
    
    # Test main endpoint
    test_hackrx_endpoint()
    
    print("\n" + "=" * 40)
    print("🎉 Test suite completed!")

if __name__ == "__main__":
    main() 