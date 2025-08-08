"""
Simple embedding and vector search module using basic text similarity.
Handles text chunking and similarity search without external API calls.
"""
import numpy as np
import re
from typing import List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils import split_text_into_chunks, count_tokens

class SimpleEmbedder:
    """Handles text similarity search using TF-IDF"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.chunks = []
        self.tfidf_matrix = None
    
    async def create_faiss_index(self, text: str):
        """
        Create similarity index from text content.
        
        Args:
            text: Input text to process
            
        Returns:
            Similarity index for search
        """
        try:
            print("🔪 Splitting text into optimized chunks...")
            # Split text into chunks
            self.chunks = split_text_into_chunks(text, chunk_size=300, overlap=100)
            
            if not self.chunks:
                raise ValueError("No chunks created from text")
            
            print(f"📦 Created {len(self.chunks)} optimized chunks")
            
            # Create TF-IDF vectors
            print("🧠 Creating TF-IDF vectors...")
            self.tfidf_matrix = self.vectorizer.fit_transform(self.chunks)
            
            print(f"✅ TF-IDF index created with {len(self.chunks)} vectors")
            return self.tfidf_matrix
            
        except Exception as e:
            print(f"❌ Error creating similarity index: {str(e)}")
            raise
    
    async def search_similar_chunks(
        self, 
        index, 
        query: str, 
        top_k: int = 5
    ) -> List[str]:
        """
        Search for similar chunks using TF-IDF similarity.
        
        Args:
            index: TF-IDF matrix
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of most similar text chunks
        """
        try:
            # Transform query to TF-IDF vector
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            
            # Get top-k indices
            top_indices = similarities.argsort()[-top_k:][::-1]
            
            # Get the actual chunks
            similar_chunks = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Similarity threshold
                    similar_chunks.append(self.chunks[idx])
            
            print(f"🔍 Found {len(similar_chunks)} similar chunks for query")
            return similar_chunks
            
        except Exception as e:
            print(f"❌ Error searching similar chunks: {str(e)}")
            return []
    
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
        """Get information about the similarity index"""
        if self.tfidf_matrix is None:
            return {"index_created": False}
        
        return {
            "index_created": True,
            "num_vectors": self.tfidf_matrix.shape[0],
            "feature_dimension": self.tfidf_matrix.shape[1],
            "index_type": "TF-IDF"
        }
