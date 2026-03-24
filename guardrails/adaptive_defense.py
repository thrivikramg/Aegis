import numpy as np
from core.database import Database
from sentence_transformers import SentenceTransformer

class AdaptiveDefenseGuardrail:
    _embedding_model = None

    def __init__(self, similarity_threshold=0.85):
        self.db = Database()
        self.similarity_threshold = similarity_threshold
        self.name = "AdaptiveDefense"
        
        # Load embedding model once globally per application lifecycle
        if AdaptiveDefenseGuardrail._embedding_model is None:
            AdaptiveDefenseGuardrail._embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def encode(self, prompt: str) -> list:
        return AdaptiveDefenseGuardrail._embedding_model.encode(prompt).tolist()

    def run(self, prompt: str) -> dict:
        embedding = self.encode(prompt)
        
        if not self.db.enabled or self.db.defense_memory is None:
            return {"blocked": False, "guardrail_name": self.name, "reason": "No DB", "risk_score": 0.0, "similarity": 0.0, "embedding": embedding}

        try:
            cursor = self.db.defense_memory.find({}, {"pattern_embedding": 1})
            stored_embeddings = [doc["pattern_embedding"] for doc in cursor if "pattern_embedding" in doc]
            
            if not stored_embeddings:
                 return {"blocked": False, "guardrail_name": self.name, "reason": "No defense memory yet", "risk_score": 0.0, "similarity": 0.0, "embedding": embedding}
                 
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity([embedding], stored_embeddings)[0]
            max_sim = float(np.max(similarities))
            
            blocked = max_sim > self.similarity_threshold
            risk_score = 1.0 if blocked else (max_sim if max_sim > 0.4 else 0.0) # normalized
            
            return {
                "blocked": blocked,
                "guardrail_name": self.name,
                "reason": f"Semantic match to known attack pattern (Sim: {max_sim:.2f})" if blocked else "Passed",
                "risk_score": risk_score,
                "similarity": max_sim,
                "embedding": embedding
            }
        except Exception as e:
            return {"blocked": False, "guardrail_name": self.name, "reason": f"Sim check error: {e}", "risk_score": 0.0, "similarity": 0.0, "embedding": embedding}
