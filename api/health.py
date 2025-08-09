"""
Health check API endpoint - separate lightweight function
"""
from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/")
async def health_check():
    """Lightweight health check endpoint"""
    return {
        "status": "healthy",
        "google_api_key_configured": bool(os.getenv("GOOGLE_API_KEY")),
        "service": "hackrx-document-qa",
        "version": "1.0.0"
    }
