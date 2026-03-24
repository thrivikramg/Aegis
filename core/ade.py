import os
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN

class AdaptiveDefenseEngine:
    def __init__(self):
        load_dotenv()
        self.mongo_uri = os.getenv("MONGODB_URI")
        
        if self.mongo_uri:
            try:
                self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=2000)
                self.db = self.client["sentinelllm"]
                self.collection = self.db["attack_memory"]
                # Quick test
                self.client.admin.command('ping')
            except Exception as e:
                print(f"[ADE] MongoDB Connection Failed: {e}")
                self.collection = None
        else:
            print("[ADE] MONGODB_URI not found. Attack Memory saving disabled.")
            self.collection = None
            
        print("[ADE] Loading SentenceTransformer...")
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.similarity_threshold = 0.82

    def check_similarity(self, prompt: str) -> dict:
        if self.collection is None:
            return {"blocked": False, "max_similarity": 0.0}
            
        try:
            embedding = self.model.encode(prompt).tolist()
            
            # Fetch all embeddings for this prototype
            cursor = self.collection.find({}, {"embedding": 1})
            stored_embeddings = [doc["embedding"] for doc in cursor if "embedding" in doc]
                    
            if not stored_embeddings:
                return {"blocked": False, "max_similarity": 0.0}
                
            similarities = cosine_similarity([embedding], stored_embeddings)[0]
            max_sim = float(np.max(similarities))
            
            return {
                "blocked": max_sim > self.similarity_threshold,
                "max_similarity": max_sim,
                "similarity_threshold": self.similarity_threshold
            }
        except Exception as e:
            print(f"[ADE] Similarity check error: {e}")
            return {"blocked": False, "max_similarity": 0.0}

    def learn_from_failure(self, prompt: str, response: str, attack_type: str, risk_score: float, guardrails_triggered: list):
        if self.collection is None:
            return
            
        try:
            embedding = self.model.encode(prompt).tolist()
            record = {
                "prompt": prompt,
                "response": response,
                "embedding": embedding,
                "attack_type": attack_type,
                "risk_score": risk_score,
                "timestamp": datetime.now(),
                "guardrails_triggered": guardrails_triggered
            }
            self.collection.insert_one(record)
            print("[ADE] Logged failure to Attack Memory DB.")
        except Exception as e:
            print(f"[ADE] Failed to save attack to memory: {e}")

    def cluster_attacks(self) -> dict:
        if self.collection is None:
            return {"clusters": 0, "patterns": []}
            
        try:
            cursor = self.collection.find({}, {"prompt": 1, "embedding": 1, "attack_type": 1})
            docs = list(cursor)
            
            if len(docs) < 2:
                return {"clusters": 0, "patterns": []}
                
            embeddings = np.array([doc["embedding"] for doc in docs if "embedding" in doc])
            prompts = [doc.get("prompt", "") for doc in docs if "embedding" in doc]
            
            if len(embeddings) < 2:
                return {"clusters": 0, "patterns": []}
                
            # DBSCAN clustering
            clustering = DBSCAN(eps=0.15, min_samples=2, metric="cosine").fit(embeddings)
            labels = clustering.labels_
            
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            
            patterns = []
            for label in set(labels):
                if label == -1:
                    continue
                cluster_prompts = [prompts[i] for i, l in enumerate(labels) if l == label]
                patterns.append({
                    "cluster_id": int(label),
                    "size": len(cluster_prompts),
                    "sample_prompts": cluster_prompts[:3]
                })
                
            # Sort patterns by size descending
            patterns.sort(key=lambda x: x["size"], reverse=True)
                
            return {"clusters": n_clusters, "patterns": patterns}
        except Exception as e:
            print(f"[ADE] Clustering error: {e}")
            return {"clusters": 0, "patterns": []}
