import sys
import os
import pandas as pd
import time
from datetime import datetime
import uuid

# Add root directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from guardrails.rebuff_detector import RebuffDetector
from guardrails.presidio_filter import PresidioFilter
from guardrails.nemo_guardrails import NeMoGuardrails
from guardrails.llama_firewall import LlamaFirewall
from guardrails.groq_judge import GroqJudgeGuardrail
from guardrails.adaptive_defense import AdaptiveDefenseGuardrail
from analysis.attack_classifier import AttackClassifier
from analysis.conversation_analyzer import ConversationAnalyzer
from analysis.attack_behavior_model import AttackBehaviorModel
from attacks.mutation_engine import MutationEngine
from core.database import Database

class GuardrailManager:
    def __init__(self):
        # 1. First Layer Semantic Guard
        self.adaptive_guard = AdaptiveDefenseGuardrail()
        
        # 2. Input Guardrails
        self.input_guards = [
            RebuffDetector(),
            PresidioFilter()
        ]
        
        # 3. Output Guardrails
        self.output_guards = [NeMoGuardrails()]
        self.agent_guards = [LlamaFirewall()]
        
        # Risk & Analysis Engines
        self.classifier = AttackClassifier()
        self.mutation_engine = MutationEngine()
        self.llm_judge = GroqJudgeGuardrail()
        self.db = Database()
        
        # V4 Deep Analysis Tracking Modules
        self.conv_analyzer = ConversationAnalyzer(self.db)
        self.behavior_model = AttackBehaviorModel(self.db)
        # Force a background model synchronization/train if needed
        if self.db.enabled and self.behavior_model.model is None:
            import threading
            threading.Thread(target=self.behavior_model.train, daemon=True).start()

    def log_result(self, record, output_path="experiments/results_v2.csv"):
        """Logs high-fidelity metrics for research analysis to flatfile."""
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            final_path = os.path.join(base_dir, output_path) if not os.path.isabs(output_path) else output_path
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            df = pd.DataFrame([record])
            file_exists = os.path.isfile(final_path)
            df.to_csv(final_path, mode='a', header=not file_exists, index=False)
        except Exception as e:
            print(f"[GuardrailManager] CSV Logging Backup Warning: {e}")

    def _run_input_phase(self, prompt, record):
        for g in self.input_guards:
            res = g.run(prompt)
            if res['blocked']:
                record.update({
                    "blocked": True,
                    "guardrail_name": res['guardrail_name'],
                    "final_response": f"[BLOCKED BY {res['guardrail_name']}]",
                    "reason": res['reason'],
                    "input_risk": res['risk_score']
                })
                return True
        return False

    def _run_output_phase(self, llm_response, record):
        for g in self.output_guards:
            res = g.run(llm_response)
            if res["blocked"]:
                record.update({
                    "blocked": True,
                    "guardrail_name": res['guardrail_name'],
                    "final_response": f"[BLOCKED BY {res['guardrail_name']}]",
                    "reason": res['reason'],
                    "output_risk": res['risk_score']
                })
                return True
        return False

    def _run_agent_phase(self, llm_response, record):
        for g in self.agent_guards:
            res = g.run(llm_response)
            if res["blocked"]:
                record.update({
                    "blocked": True,
                    "guardrail_name": res['guardrail_name'],
                    "final_response": f"[BLOCKED BY {res['guardrail_name']}]",
                    "reason": res['reason']
                })
                return True
        return False

    def run_full_pipeline(self, prompt, llm_interface, model_name="local-llm", attack_type="unknown", conversation_id=None):
        """
        Executes the self-learning guardrail pipeline with V4 6-layer dynamic risk scoring.
        """
        attack_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Generate Embeddings immediately
        embedding = self.adaptive_guard.encode(prompt)
        
        # Deduplication Check
        dup_id = self.db.check_duplicate(embedding, threshold=0.95)
        
        # V4 Multi-Turn Conversational Escalation State check
        conv_res = self.conv_analyzer.analyze_turn(conversation_id, prompt)
        conv_risk = conv_res["conversation_risk_score"]
        
        # Attack Classification
        class_res = self.classifier.classify(prompt)
        inferred_type = class_res["attack_type"] if attack_type == "unknown" else attack_type
        class_conf = class_res["classification_confidence"]
        class_severity = class_res["severity"]

        record = {
            "timestamp": datetime.now().isoformat(),
            "model": model_name,
            "attack_type": inferred_type,
            "prompt": prompt,
            "blocked": False,
            "guardrail_name": None,
            "final_response": "",
            "response_time": 0.0,
            "input_risk": 0.0,
            "output_risk": 0.0,
            "ade_similarity": 0.0,
            "risk_score": 0.0
        }

        # 1) Adaptive Defense Check (Runs First)
        ade_res = self.adaptive_guard.run(prompt) # Computes vs defense_memory
        record["ade_similarity"] = ade_res["similarity"]
        guardrail_weight = 0.0
        judge_score = 0.0
        
        if ade_res["blocked"]:
            record.update({
                "blocked": True,
                "guardrail_name": ade_res["guardrail_name"],
                "final_response": f"[BLOCKED BY {ade_res['guardrail_name']}]",
                "reason": ade_res["reason"],
                "input_risk": ade_res["risk_score"]
            })
            guardrail_weight = 1.0

        # Custom Guardrails & LLM Judge Check
        if not record["blocked"]:
            if self._run_input_phase(prompt, record):
                guardrail_weight = 1.0
            
            judge_res = self.llm_judge.run(prompt)
            if judge_res["blocked"]:
                judge_score = 1.0
                if not record["blocked"]:
                    record.update({
                        "blocked": True,
                        "guardrail_name": judge_res["guardrail_name"],
                        "final_response": f"[BLOCKED BY {judge_res['guardrail_name']}]",
                        "reason": judge_res["reason"],
                        "input_risk": judge_res["risk_score"]
                    })

        # V4 Behavior ML Detection Model
        behavior_prob = self.behavior_model.predict(prompt, embedding, ade_res["similarity"])
        
        # Attack Family Risk (V5 Heuristic metric)
        # Inferred natively combining classification severity with known behavior model probabilities globally
        attack_family_risk = min(1.0, class_severity * 0.5 + behavior_prob * 0.5)

        # V5 Dynamic Risk Scoring System Execution
        # 0.25(sem) + 0.20(guard) + 0.20(judge) + 0.15(behave) + 0.10(conv) + 0.10(family)
        risk_score = (
            (0.25 * ade_res["similarity"]) + 
            (0.20 * guardrail_weight) + 
            (0.20 * judge_score) + 
            (0.15 * behavior_prob) + 
            (0.10 * conv_risk) +
            (0.10 * attack_family_risk)
        )
        record["risk_score"] = risk_score
        
        if risk_score > 0.8 and not record["blocked"]:
            record["blocked"] = True
            record["guardrail_name"] = "V5_RiskScoringSystem"
            record["reason"] = f"V5 Aggregated Risk Score ({risk_score:.2f}) natively exceeded absolute boundary limit."
            record["final_response"] = "[BLOCKED BY V5_RiskScoringSystem]"
            
        # Target Model Generation
        if not record["blocked"]:
            llm_response = llm_interface.generate_response(prompt)
            
            self.db.log_model_response({
                "response_id": str(uuid.uuid4()),
                "attack_id": attack_id,
                "model_name": model_name,
                "model_response": llm_response,
                "latency_ms": time.time() - start_time,
                "tokens_used": 0 # Proxy
            })
            
            output_blocked = self._run_output_phase(llm_response, record)
            if not output_blocked:
                output_blocked = self._run_agent_phase(llm_response, record)
                
            if output_blocked:
                # Caught post-generation! Reinforce defenses for next time
                self.db.log_defense_memory({
                    "pattern_embedding": embedding,
                    "attack_type": inferred_type,
                    "recommended_action": "BLOCK",
                    "confidence": risk_score if risk_score > 0.6 else 0.95,
                    "created_from_attack": attack_id
                })
            else:
                record["final_response"] = llm_response
                
                # TOTAL BYPASS -> Attack Succeeded natively
                # Self-Improving Evolution Loop: Sub-spawn mutated variants
                self.mutation_engine.generate_mutations(prompt, attack_id)
                self.db.log_defense_memory({
                    "pattern_embedding": embedding,
                    "attack_type": inferred_type,
                    "recommended_action": "BLOCK",
                    "confidence": 1.0, # Known vulnerable vector
                    "created_from_attack": attack_id
                })
                
                # Immediately retrain ML behavior algorithms asynchronously to adapt to the zero-day
                import threading
                threading.Thread(target=self.behavior_model.train, daemon=True).start()

        record["response_time"] = time.time() - start_time
        
        # --- DATABASE LOGGING ---
        if dup_id:
            # Deduplication Optimization
            self.db._async_run(
                self.db.attacks.insert_one, 
                {"attack_id": attack_id, "duplicate_of_attack_id": dup_id, "timestamp": datetime.now()}
            )
        else:
            self.db.log_attack({
                "attack_id": attack_id,
                "timestamp": datetime.now(),
                "attack_prompt": prompt,
                "embedding_vector": embedding,
                "attack_type": inferred_type,
                "classification_confidence": class_conf,
                "model_response": record["final_response"],
                "guardrail_triggered": record["guardrail_name"],
                "similarity_score": ade_res["similarity"],
                "risk_score": risk_score,
                "success": not record["blocked"],
                "cluster_id": None
            })
            
        self.db.log_guardrail_result({
            "attack_id": attack_id,
            "rebuff_detector": record["guardrail_name"] == "Rebuff (Injection Detector)",
            "presidio_filter": record["guardrail_name"] == "Presidio (PII Filter)",
            "judge_model_flag": judge_score > 0,
            "similarity_block": record["guardrail_name"] == "AdaptiveDefense",
            "final_action": "BLOCKED" if record["blocked"] else "ALLOWED",
            "risk_score": risk_score
        })
        
        self.db.log_attack_outcome({
            "attack_id": attack_id,
            "success": not record["blocked"],
            "attack_category": inferred_type,
            "defense_triggered": record["guardrail_name"] or "None",
            "severity": class_severity
        })
        
        if record["blocked"]:
            self.db.log_defense_log(
                prompt=prompt,
                triggered=record["guardrail_name"],
                similarity=ade_res["similarity"],
                risk=risk_score,
                explanation=record.get("reason", "Automatically isolated and quarantined.")
            )
            
        if conversation_id:
            # Sync the context graph natively before progressing 
            self.db.log_conversation_turn({
                "conversation_id": conversation_id,
                "timestamp": datetime.now(),
                "user_prompt": prompt,
                "model_response": record["final_response"],
                "embedding_vector": embedding,
                "attack_probability": behavior_prob,
                "risk_score": risk_score
            })
        # ------------------------
        
        self.log_result(record)
        return record
