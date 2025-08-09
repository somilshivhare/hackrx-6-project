"""
Ultra-lightweight embedding and vector search module using pure Python.
Handles text chunking and similarity search without any heavy dependencies.
"""
import re
import math
from collections import Counter
from typing import List, Tuple, Optional, Dict

from utils import split_text_into_chunks, count_tokens

class SimpleEmbedder:
    """Handles text similarity search using lightweight TF-IDF"""
    
    def __init__(self):
        self.chunks = []
        self.vocabulary = {}
        self.tfidf_matrix = None
        self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization and stop word removal"""
        words = re.findall(r'\b\w+\b', text.lower())
        return [w for w in words if w not in self.stop_words and len(w) > 2]
    
    def _build_vocabulary(self, chunks: List[str]) -> Dict[str, int]:
        """Build vocabulary from all chunks"""
        all_words = set()
        for chunk in chunks:
            words = self._tokenize(chunk)
            all_words.update(words)
        return {word: idx for idx, word in enumerate(sorted(all_words))}
    
    def _compute_tf_idf(self, chunks: List[str]) -> List[List[float]]:
        """Compute TF-IDF matrix using pure Python lists"""
        vocab_size = len(self.vocabulary)
        num_docs = len(chunks)
        
        # Initialize TF-IDF matrix as list of lists
        tfidf_matrix = [[0.0 for _ in range(vocab_size)] for _ in range(num_docs)]
        
        # Document frequency for each term
        df = [0 for _ in range(vocab_size)]
        
        # Compute term frequencies and document frequencies
        for doc_idx, chunk in enumerate(chunks):
            words = self._tokenize(chunk)
            word_counts = Counter(words)
            doc_length = len(words)
            
            # Track which terms appear in this document
            terms_in_doc = set()
            
            for word, count in word_counts.items():
                if word in self.vocabulary:
                    term_idx = self.vocabulary[word]
                    # TF: term frequency
                    tf = count / doc_length if doc_length > 0 else 0
                    tfidf_matrix[doc_idx][term_idx] = tf
                    
                    # Track for DF calculation
                    terms_in_doc.add(term_idx)
            
            # Update document frequencies
            for term_idx in terms_in_doc:
                df[term_idx] += 1
        
        # Compute IDF and final TF-IDF
        for term_idx in range(vocab_size):
            if df[term_idx] > 0:
                idf = math.log(num_docs / df[term_idx])
                for doc_idx in range(num_docs):
                    tfidf_matrix[doc_idx][term_idx] *= idf
        
        return tfidf_matrix

    async def create_faiss_index(self, text: str):
        """
        Create similarity index from text content using lightweight TF-IDF.
        
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
            
            # Build vocabulary
            print("📚 Building vocabulary...")
            self.vocabulary = self._build_vocabulary(self.chunks)
            
            # Create TF-IDF vectors
            print("🧠 Creating lightweight TF-IDF vectors...")
            self.tfidf_matrix = self._compute_tf_idf(self.chunks)
            
            print(f"✅ TF-IDF index created with {len(self.chunks)} vectors")
            return self.tfidf_matrix
            
        except Exception as e:
            print(f"❌ Error creating similarity index: {str(e)}")
            raise
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

    def _query_to_vector(self, query: str) -> List[float]:
        """Convert query to TF-IDF vector"""
        words = self._tokenize(query)
        word_counts = Counter(words)
        query_length = len(words)
        
        query_vector = [0.0 for _ in range(len(self.vocabulary))]
        
        for word, count in word_counts.items():
            if word in self.vocabulary:
                term_idx = self.vocabulary[word]
                tf = count / query_length if query_length > 0 else 0
                query_vector[term_idx] = tf
        
        return query_vector

    async def search_similar_chunks(
        self, 
        index, 
        query: str, 
        top_k: int = 5
    ) -> List[str]:
        """
        Search for similar chunks using lightweight TF-IDF similarity.
        
        Args:
            index: TF-IDF matrix
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of most similar text chunks
        """
        try:
            # Transform query to TF-IDF vector
            query_vector = self._query_to_vector(query)
            
            # Calculate similarities with all chunks
            similarities = []
            for i in range(len(self.tfidf_matrix)):
                chunk_vector = self.tfidf_matrix[i]
                similarity = self._cosine_similarity(query_vector, chunk_vector)
                similarities.append((similarity, i))
            
            # Sort by similarity and get top-k indices
            similarities.sort(reverse=True, key=lambda x: x[0])
            top_indices = [idx for _, idx in similarities[:top_k]]
            
            # Get the actual chunks
            similar_chunks = []
            for idx in top_indices:
                # Find the similarity score for this index
                sim_score = next((sim for sim, i in similarities if i == idx), 0)
                if sim_score > 0.1:  # Similarity threshold
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
            "num_vectors": len(self.tfidf_matrix),
            "feature_dimension": len(self.tfidf_matrix[0]) if self.tfidf_matrix else 0,
            "vocabulary_size": len(self.vocabulary),
            "index_type": "Pure Python TF-IDF"
        }
