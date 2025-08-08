"""
Embedding and vector search module using OpenAI embeddings and FAISS.
Handles text chunking, embedding generation, and similarity search.
"""
import openai
import faiss
import numpy as np
import asyncio
from typing import List, Tuple, Optional
import os
from dotenv import load_dotenv

from utils import split_text_into_chunks, count_tokens

# Load environment variables
load_dotenv()

class Embedder:
    """Handles text embedding and FAISS vector search"""
    
    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.embedding_model = "text-embedding-3-large"
        self.dimension = 3072  # text-embedding-3-large dimension
        
        # FAISS index
        self.index = None
        self.chunks = []
    
    async def create_faiss_index(self, text: str) -> faiss.Index:
        """
        Create optimized FAISS index from text content with enhanced chunking.
        
        Args:
            text: Input text to process
            
        Returns:
            FAISS index for similarity search
        """
        try:
            print("🔪 Splitting text into optimized chunks...")
            # Use smaller, more focused chunks for better precision
            self.chunks = split_text_into_chunks(text, chunk_size=300, overlap=100)
            
            if not self.chunks:
                raise ValueError("No chunks created from text")
            
            print(f"📦 Created {len(self.chunks)} optimized chunks")
            
            # Generate embeddings for chunks
            print("🧠 Generating embeddings...")
            embeddings = await self._generate_embeddings(self.chunks)
            
            if not embeddings:
                raise ValueError("Failed to generate embeddings")
            
            # Create FAISS index with optimized parameters
            print("🔍 Creating optimized FAISS index...")
            self.index = self._create_faiss_index(embeddings)
            
            print(f"✅ Optimized FAISS index created with {len(embeddings)} vectors")
            return self.index
            
        except Exception as e:
            print(f"❌ Error creating FAISS index: {str(e)}")
            raise
    
    async def search_similar_chunks(
        self, 
        index: faiss.Index, 
        query: str, 
        top_k: int = 5
    ) -> List[str]:
        """
        Search for similar chunks using optimized FAISS parameters.
        
        Args:
            index: FAISS index
            query: Search query
            top_k: Number of top results to return (increased for better coverage)
            
        Returns:
            List of most similar text chunks
        """
        try:
            # Generate embedding for query
            query_embedding = await self._generate_embeddings([query])
            
            if not query_embedding:
                raise ValueError("Failed to generate query embedding")
            
            # Search in FAISS index with optimized parameters
            query_vector = np.array(query_embedding, dtype=np.float32)
            
            # Perform similarity search with more results for better coverage
            distances, indices = index.search(query_vector, min(top_k, len(self.chunks)))
            
            # Get the actual chunks and filter by similarity threshold
            similar_chunks = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.chunks):
                    # Only include chunks with good similarity (distance > 0.7)
                    if distances[0][i] > 0.7:
                        similar_chunks.append(self.chunks[idx])
            
            print(f"🔍 Found {len(similar_chunks)} high-quality similar chunks for query")
            return similar_chunks
            
        except Exception as e:
            print(f"❌ Error searching similar chunks: {str(e)}")
            return []
    
    async def _generate_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Generate embeddings using OpenAI API.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            # Process in batches to avoid rate limits
            batch_size = 10
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Generate embeddings for batch
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.embeddings.create(
                        model=self.embedding_model,
                        input=batch
                    )
                )
                
                # Extract embeddings
                batch_embeddings = [embedding.embedding for embedding in response.data]
                all_embeddings.extend(batch_embeddings)
                
                # Small delay to respect rate limits
                await asyncio.sleep(0.1)
            
            return all_embeddings
            
        except Exception as e:
            print(f"❌ Error generating embeddings: {str(e)}")
            return None
    
    def _create_faiss_index(self, embeddings: List[List[float]]) -> faiss.Index:
        """
        Create FAISS index from embeddings.
        
        Args:
            embeddings: List of embedding vectors
            
        Returns:
            FAISS index
        """
        try:
            # Convert to numpy array
            embeddings_array = np.array(embeddings, dtype=np.float32)
            
            # Create FAISS index
            # Using IndexFlatIP for inner product (cosine similarity)
            index = faiss.IndexFlatIP(self.dimension)
            
            # Normalize vectors for cosine similarity
            faiss.normalize_L2(embeddings_array)
            
            # Add vectors to index
            index.add(embeddings_array)
            
            return index
            
        except Exception as e:
            print(f"❌ Error creating FAISS index: {str(e)}")
            raise
    
    def get_chunk_info(self) -> dict:
        """Get information about the processed chunks"""
        if not self.chunks:
            return {"num_chunks": 0, "total_tokens": 0}
        
        total_tokens = sum(count_tokens(chunk) for chunk in self.chunks)
        
        return {
            "num_chunks": len(self.chunks),
            "total_tokens": total_tokens,
            "avg_chunk_tokens": total_tokens // len(self.chunks) if self.chunks else 0
        }
    
    def get_index_info(self) -> dict:
        """Get information about the FAISS index"""
        if not self.index:
            return {"index_created": False}
        
        return {
            "index_created": True,
            "num_vectors": self.index.ntotal,
            "dimension": self.index.d,
            "index_type": type(self.index).__name__
        } 