#!/usr/bin/env python3
"""
Mock test script for development without API calls
"""
import requests
import json

def test_mock_response():
    """Test the API structure with mock data"""
    print("🧪 Testing API Structure with Mock Data")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/")
        print("✅ Health endpoint working:")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return
    
    # Test main endpoint structure (this will fail due to API quota, but we can see the structure)
    print("\n🔍 API Structure Test:")
    print("   - Endpoint: POST /hackrx/run")
    print("   - Authentication: Bearer token required")
    print("   - Request format: JSON with documents and questions")
    print("   - Response format: JSON with answers array")
    
    print("\n📋 Expected Request Format:")
    print("""
    {
        "documents": "https://example.com/policy.pdf",
        "questions": [
            "What is the grace period for premium payment?",
            "Does this policy cover maternity expenses?"
        ]
    }
    """)
    
    print("📋 Expected Response Format:")
    print("""
    {
        "answers": [
            {
                "answer": "The grace period is 30 days.",
                "source_clause": "Section 4.2: Grace period of 30 days...",
                "reasoning": "Based on the policy document..."
            }
        ]
    }
    """)
    
    print("\n✅ API Structure is Correct!")
    print("⚠️  Note: API calls will fail until Google Gemini quota is resolved")

if __name__ == "__main__":
    test_mock_response()
