import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import threading

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        load_dotenv()
        self.mongo_uri = os.getenv("MONGODB_URI")
        self.db_name = "aegis_db"
        self.enabled = False
        
        if self.mongo_uri:
            try:
                self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=2000)
                self.db = self.client[self.db_name]
                
                # Phase 1 & 2 Collections
                self.attacks = self.db["attacks"]
                self.model_responses = self.db["model_responses"]
                self.guardrail_results = self.db["guardrail_results"]
                self.attack_outcomes = self.db["attack_outcomes"]
                self.defense_memory = self.db["defense_memory"]
                self.security_metrics = self.db["security_metrics"]
                self.conversations = self.db["conversations"]
                
                # Phase 3 Collections (V3)
                self.mutated_attacks = self.db["mutated_attacks"]
                self.defense_evaluation = self.db["defense_evaluation"]
                self.defense_logs = self.db["defense_logs"]
                
                # Phase 4 (V4) Collections 
                self.conversation_memory = self.db["conversation_memory"]
                self.threat_clusters = self.db["threat_clusters"]
                
                # Phase 5 (V5) Autonomous Collections
                self.generated_attacks = self.db["generated_attacks"]
                self.attack_simulation_results = self.db["attack_simulation_results"]
                self.model_security_scores = self.db["model_security_scores"]
                self.stress_test_results = self.db["stress_test_results"]
                self.defense_rules = self.db["defense_rules"]
                
                self.client.admin.command('ping')
                self.enabled = True
                print("[Database] V3 Async Architecture Initialized.")
            except Exception as e:
                print(f"[Database] Connection Error: {e}")

    def _async_run(self, func, *args, **kwargs):
        """Executes database commands in a fire-and-forget background thread."""
        if not self.enabled: return
        try:
            t = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
            t.start()
        except Exception as e:
            print(f"Async DB Error: {e}")

    # ===== ASYNC WRAPPERS =====
    
    def log_attack(self, doc: dict):
        self._async_run(self._log_attack_sync, doc)
        
    def log_defense_log(self, prompt, triggered, similarity, risk, explanation):
        self._async_run(self.defense_logs.insert_one, {
            "prompt": prompt, "guardrail_triggered": triggered,
            "similarity_score": similarity, "risk_score": risk, 
            "explanation_text": explanation, "timestamp": datetime.now()
        })
        
    def log_model_response(self, doc: dict):
        self._async_run(self.model_responses.insert_one, doc)
        
    def log_guardrail_result(self, doc: dict):
        self._async_run(self.guardrail_results.insert_one, doc)
        
    def log_attack_outcome(self, doc: dict):
        self._async_run(self.attack_outcomes.insert_one, doc)
        
    def log_defense_memory(self, doc: dict):
        self._async_run(self.defense_memory.insert_one, doc)

    def update_security_metrics(self, doc_query: dict, update_fields: dict):
        if not self.enabled: return
        self._async_run(self.security_metrics.update_one, doc_query, {"$set": update_fields}, upsert=True)

    def log_conversation_turn(self, doc: dict):
        if not self.enabled: return
        self._async_run(self.conversation_memory.insert_one, doc)
        
    def log_threat_cluster(self, doc: dict):
        if not self.enabled: return
        self._async_run(self.threat_clusters.insert_one, doc)
        
    def log_conversation_msg(self, conv_id, msg, risk):
        if not self.enabled or not conv_id: return
        self._async_run(self.conversations.update_one, 
            {"conversation_id": conv_id},
            {"$push": {"messages": msg, "risk_progression": risk}}, 
            upsert=True
        )

    # ===== SYNC METHODS =====

    def _log_attack_sync(self, doc):
        try:
            self.attacks.insert_one(doc)
        except Exception as e:
            pass

    def check_duplicate(self, embedding_vector, threshold=0.95):
        """Synchronously checks if an attack is a duplicate before proceeding."""
        if not self.enabled or not embedding_vector: return None
        try:
            import numpy as np
            from sklearn.metrics.pairwise import cosine_similarity
            
            cursor = self.attacks.find({}, {"attack_id": 1, "embedding_vector": 1})
            stored = list(cursor)
            if not stored: return None
            
            embeddings = [d["embedding_vector"] for d in stored if d.get("embedding_vector")]
            ids = [d["attack_id"] for d in stored if d.get("embedding_vector")]
            
            if not embeddings: return None
            
            sims = cosine_similarity([embedding_vector], embeddings)[0]
            max_idx = np.argmax(sims)
            
            if sims[max_idx] > threshold:
                return ids[max_idx]
        except Exception:
            pass
        return None
