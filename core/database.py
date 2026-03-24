import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

class Database:
    def __init__(self):
        load_dotenv()
        self.mongo_uri = os.getenv("MONGODB_URI")
        self.db_name = "sentinelllm_db"
        self.enabled = False
        
        if self.mongo_uri:
            try:
                self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=2000)
                self.db = self.client[self.db_name]
                
                # Collections initialization
                self.attacks = self.db["attacks"]
                self.model_responses = self.db["model_responses"]
                self.guardrail_results = self.db["guardrail_results"]
                self.attack_outcomes = self.db["attack_outcomes"]
                self.defense_memory = self.db["defense_memory"]
                self.security_metrics = self.db["security_metrics"]
                self.conversations = self.db["conversations"]
                
                # Silent Ping to test connection
                self.client.admin.command('ping')
                self.enabled = True
                print("[Database] MongoDB Initialization Successful - 7 Collections Online.")
            except Exception as e:
                print(f"[Database] Connection Error: {e}")
        else:
            print("[Database] No MONGODB_URI found. DB Logging is disabled.")

    def log_attack(self, attack_id, prompt, attack_type, source="dashboard", conv_id=None, embedding=None, similar_ids=None):
        if not self.enabled: return
        try:
            self.attacks.insert_one({
                "attack_id": attack_id,
                "timestamp": datetime.now(),
                "attack_prompt": prompt,
                "attack_type": attack_type,
                "attack_source": source,
                "conversation_id": conv_id,
                "embedding_vector": embedding,
                "similar_attack_ids": similar_ids or []
            })
        except Exception as e:
            print(f"[Database] log_attack error: {e}")

    def log_model_response(self, response_id, attack_id, model_name, response, latency, tokens=0):
        if not self.enabled: return
        try:
            self.model_responses.insert_one({
                "response_id": response_id,
                "attack_id": attack_id,
                "model_name": model_name,
                "model_response": response,
                "latency_ms": latency,
                "tokens_used": tokens
            })
        except Exception as e:
            print(f"[Database] log_model_response error: {e}")

    def log_guardrail_result(self, attack_id, rebuff, presidio, judge, similarity, final_action, risk):
        if not self.enabled: return
        try:
            self.guardrail_results.insert_one({
                "attack_id": attack_id,
                "rebuff_detector": rebuff,
                "presidio_filter": presidio,
                "judge_model_flag": judge,
                "similarity_block": similarity,
                "final_action": final_action,
                "risk_score": risk
            })
        except Exception as e:
            print(f"[Database] log_guardrail_result error: {e}")

    def log_attack_outcome(self, attack_id, success, category, defense, severity):
        if not self.enabled: return
        try:
            self.attack_outcomes.insert_one({
                "attack_id": attack_id,
                "success": success,
                "attack_category": category,
                "defense_triggered": defense,
                "severity": severity
            })
        except Exception as e:
            print(f"[Database] log_attack_outcome error: {e}")

    def log_defense_memory(self, embedding, attack_type, action, confidence, from_attack_id):
        if not self.enabled: return
        try:
            self.defense_memory.insert_one({
                "pattern_embedding": embedding,
                "attack_type": attack_type,
                "recommended_action": action,
                "confidence": confidence,
                "created_from_attack": from_attack_id
            })
        except Exception as e:
            print(f"[Database] log_defense_memory error: {e}")

    def update_security_metrics(self, date_str, total_tested, total_blocked, success_rate, top_attack):
        if not self.enabled: return
        try:
            self.security_metrics.update_one(
                {"date": date_str},
                {"$set": {
                    "attacks_tested": total_tested,
                    "attacks_blocked": total_blocked,
                    "attack_success_rate": success_rate,
                    "top_attack_type": top_attack
                }},
                upsert=True
            )
        except Exception as e:
            print(f"[Database] update_security_metrics error: {e}")

    def log_conversation_msg(self, conv_id, msg, risk):
        if not self.enabled or not conv_id: return
        try:
            self.conversations.update_one(
                {"conversation_id": conv_id},
                {"$push": {
                    "messages": msg, 
                    "risk_progression": risk
                }},
                upsert=True
            )
        except Exception as e:
            print(f"[Database] log_conversation error: {e}")
