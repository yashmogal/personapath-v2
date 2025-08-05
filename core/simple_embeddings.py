"""
Simple embeddings fallback for environments without sentence-transformers
"""
import numpy as np
from typing import List
import hashlib
import re

class SimpleEmbeddings:
    """Basic embeddings using TF-IDF-like approach"""
    
    def __init__(self, model_name="simple"):
        self.model_name = model_name
        self.vocab = {}
        self.idf = {}
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Simple document embedding using word frequency"""
        if not texts:
            return []
            
        # Build vocabulary from all texts
        all_words = set()
        doc_words = []
        
        for text in texts:
            # Clean and tokenize text
            text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
            words = [w for w in text_clean.split() if len(w) > 2]  # Filter short words
            doc_words.append(words)
            all_words.update(words)
        
        vocab = sorted(list(all_words))[:384]  # Limit vocabulary size
        embeddings = []
        
        for words in doc_words:
            # Create TF-IDF-like vector
            vector = [0.0] * len(vocab)
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            # Calculate term frequency
            for i, vocab_word in enumerate(vocab):
                if vocab_word in word_counts and len(words) > 0:
                    vector[i] = word_counts[vocab_word] / len(words)
            
            # Normalize vector
            norm = sum(x*x for x in vector) ** 0.5
            if norm > 0:
                vector = [x/norm for x in vector]
            
            # Ensure minimum dimensions
            while len(vector) < 384:
                vector.append(0.0)
            
            embeddings.append(vector[:384])  # Limit to 384 dimensions
        
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Simple query embedding"""
        if not text.strip():
            return [0.0] * 384
        return self.embed_documents([text])[0]