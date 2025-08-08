"""
Document parser for extracting text from PDF documents.
Handles PDF downloading and text extraction using PDFPlumber.
"""
import pdfplumber
import requests
import tempfile
import os
from typing import Optional
import asyncio
from urllib.parse import urlparse

class DocumentParser:
    """Handles PDF document parsing and text extraction"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    async def parse_pdf_from_url(self, url: str) -> Optional[str]:
        """
        Download PDF from URL and extract text content.
        
        Args:
            url: URL to the PDF document
            
        Returns:
            Extracted text content or None if failed
        """
        try:
            # Validate URL
            if not self._is_valid_pdf_url(url):
                raise ValueError(f"Invalid PDF URL: {url}")
            
            # Download PDF
            print(f"📥 Downloading PDF from: {url}")
            pdf_content = await self._download_pdf(url)
            
            if not pdf_content:
                raise ValueError("Failed to download PDF content")
            
            # Extract text from PDF
            print("📖 Extracting text from PDF...")
            text_content = await self._extract_text_from_pdf_content(pdf_content)
            
            if not text_content:
                raise ValueError("No text content extracted from PDF")
            
            print(f"✅ Successfully extracted {len(text_content)} characters")
            return text_content
            
        except Exception as e:
            print(f"❌ Error parsing PDF from URL: {str(e)}")
            return None
    
    def _is_valid_pdf_url(self, url: str) -> bool:
        """Check if URL points to a valid PDF file"""
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme in ['http', 'https'] and
                parsed.path.lower().endswith('.pdf')
            )
        except:
            return False
    
    async def _download_pdf(self, url: str) -> Optional[bytes]:
        """Download PDF content from URL"""
        try:
            # Use aiohttp for async requests in production
            # For now, using requests with asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: requests.get(url, timeout=30, stream=True)
            )
            
            response.raise_for_status()
            
            # Read content in chunks to handle large files
            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
            
            return content
            
        except Exception as e:
            print(f"❌ Error downloading PDF: {str(e)}")
            return None
    
    async def _extract_text_from_pdf_content(self, pdf_content: bytes) -> Optional[str]:
        """Extract text from PDF content using PDFPlumber"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name
            
            try:
                # Extract text using PDFPlumber
                extracted_text = ""
                
                with pdfplumber.open(temp_file_path) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        print(f"Processing page {page_num + 1}/{len(pdf.pages)}")
                        
                        # Extract text from page
                        page_text = page.extract_text()
                        
                        if page_text:
                            # Clean and normalize text
                            cleaned_text = self._clean_page_text(page_text)
                            extracted_text += cleaned_text + "\n\n"
                
                return extracted_text.strip()
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            print(f"❌ Error extracting text from PDF: {str(e)}")
            return None
    
    def _clean_page_text(self, text: str) -> str:
        """Clean and normalize extracted page text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Remove common PDF artifacts
        text = text.replace('\x00', '')  # Null bytes
        text = text.replace('\x0c', ' ')  # Form feed
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove multiple consecutive line breaks
        import re
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def extract_metadata(self, pdf_content: bytes) -> dict:
        """Extract metadata from PDF (optional enhancement)"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name
            
            try:
                with pdfplumber.open(temp_file_path) as pdf:
                    metadata = {
                        'num_pages': len(pdf.pages),
                        'title': pdf.metadata.get('Title', ''),
                        'author': pdf.metadata.get('Author', ''),
                        'subject': pdf.metadata.get('Subject', ''),
                        'creator': pdf.metadata.get('Creator', '')
                    }
                    return metadata
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            print(f"❌ Error extracting metadata: {str(e)}")
            return {} 