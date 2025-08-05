"""
Simple embeddings fallback for environments without sentence-transformers
"""
import numpy as np
from typing import List
import hashlib

class SimpleEmbeddings:
    """Basic embeddings using TF-IDF-like approach"""
    
    def __init__(self, model_name="simple"):
        self.model_name = model_name
        self.vocab = {}
        self.idf = {}
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Simple document embedding using word frequency"""
        # Build vocabulary
        all_words = set()
        doc_words = []
        
        for text in texts:
            words = text.lower().split()
            doc_words.append(words)
            all_words.update(words)
        
        vocab = list(all_words)
        embeddings = []
        
        for words in doc_words:
            # Create simple TF vector
            vector = [0.0] * min(384, len(vocab))  # Limit to 384 dimensions
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            for i, vocab_word in enumerate(vocab[:384]):
                if vocab_word in word_counts:
                    vector[i] = word_counts[vocab_word] / len(words)
            
            # Normalize
            norm = sum(x*x for x in vector) ** 0.5
            if norm > 0:
                vector = [x/norm for x in vector]
            
            embeddings.append(vector)
        
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Simple query embedding"""
        return self.embed_documents([text])[0]