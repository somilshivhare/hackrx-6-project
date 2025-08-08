#!/usr/bin/env python3
"""
Test script to verify deployment
"""
import requests
import json

def test_deployment(url):
    """Test the deployed API"""
    print(f"🧪 Testing deployment at: {url}")
    
    # Test health endpoint
    try:
        health_response = requests.get(f"{url}/")
        print(f"✅ Health check: {health_response.status_code}")
        print(f"Response: {health_response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test main endpoint
    test_payload = {
        "documents": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        "questions": [
            "What is this document about?",
            "What is the purpose of this PDF?"
        ]
    }
    
    headers = {
        "Authorization": "Bearer c3d64f143a0f199ddaa8e69856eaaeffa4d101bf633c771f581e441ba15ae106",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{url}/hackrx/run", json=test_payload, headers=headers)
        print(f"✅ Main endpoint: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Number of answers: {len(result.get('answers', []))}")
            return True
        else:
            print(f"❌ Main endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Main endpoint failed: {e}")
        return False

if __name__ == "__main__":
    # Replace with your actual deployment URL
    deployment_url = "https://your-app-name.onrender.com"
    
    print("🚀 Testing HackRx Deployment")
    print("=" * 40)
    
    success = test_deployment(deployment_url)
    
    if success:
        print("\n🎉 Deployment is working correctly!")
        print("✅ Ready for HackRx submission!")
    else:
        print("\n❌ Deployment has issues. Please check:")
        print("1. Environment variables are set correctly")
        print("2. Google API key is valid")
        print("3. All dependencies are installed")
