import sys
import os
import pandas as pd
import time
from datetime import datetime

# Add root directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from guardrails.rebuff_detector import RebuffDetector
from guardrails.presidio_filter import PresidioFilter
from guardrails.nemo_guardrails import NeMoGuardrails
from guardrails.llama_firewall import LlamaFirewall
from core.ade import AdaptiveDefenseEngine
from guardrails.groq_judge import GroqJudgeGuardrail
from core.database import Database
import uuid

class GuardrailManager:
    def __init__(self):
        # Initialize the security layers
        # Input Guardrails
        self.input_guards = [
            RebuffDetector(),
            PresidioFilter()
        ]
        
        # Output Guardrails
        self.output_guards = [
            # from guardrails.nemo_guardrails import NeMoGuardrails
            # We'll import them locally here to avoid circular imports or missing files
            # NeMoGuardrails(),
            # from guardrails.llama_firewall import LlamaFirewall
            # LlamaFirewall()
        ]
        # Fixed imports below after correcting class placement
        from guardrails.nemo_guardrails import NeMoGuardrails
        from guardrails.llama_firewall import LlamaFirewall
        self.output_guards = [NeMoGuardrails()]
        self.agent_guards = [LlamaFirewall()]
        
        self.ade = AdaptiveDefenseEngine()
        self.llm_judge = GroqJudgeGuardrail()
        self.db = Database()

    def log_result(self, record, output_path="experiments/results_v2.csv"):
        """Logs high-fidelity metrics for research analysis."""
        df = pd.DataFrame([record])
        file_exists = os.path.isfile(output_path)
        df.to_csv(output_path, mode='a', header=not file_exists, index=False)

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

    def run_full_pipeline(self, prompt, llm_interface, model_name="local-llm", attack_type="unknown"):
        """
        Executes the entire guardrail pipeline with ADE functionality.
        """
        attack_id = str(uuid.uuid4())
        record = {
            "timestamp": datetime.now().isoformat(),
            "model": model_name,
            "attack_type": attack_type,
            "prompt": prompt,
            "blocked": False,
            "guardrail_name": None,
            "final_response": "",
            "response_time": 0.0,
            "input_risk": 0.0,
            "output_risk": 0.0,
            "ade_similarity": 0.0
        }
        
        start_time = time.time()
        
        # 1) ADE Memory Similarity Check
        ade_res = self.ade.check_similarity(prompt)
        record["ade_similarity"] = ade_res["max_similarity"]
        
        if ade_res["blocked"]:
            record.update({
                "blocked": True,
                "guardrail_name": "AdaptiveDefenseEngine",
                "final_response": f"[BLOCKED BY ADE MEMORY] Similarity context trigger.",
                "reason": f"High similarity ({ade_res['max_similarity']:.2f}) to known attacks.",
                "input_risk": 100.0
            })
        elif not self._run_input_phase(prompt, record): # 2) Standard Input Guardrails
            # 3) Groq LLM-as-Judge
            judge_res = self.llm_judge.run(prompt)
            if judge_res["blocked"]:
                record.update({
                    "blocked": True,
                    "guardrail_name": judge_res["guardrail_name"],
                    "final_response": f"[BLOCKED BY {judge_res['guardrail_name']}]",
                    "reason": judge_res["reason"],
                    "input_risk": judge_res["risk_score"]
                })
            else:
                # 4) Target Model Generation
                llm_response = llm_interface.generate_response(prompt)
                
                self.db.log_model_response(
                    response_id=str(uuid.uuid4()),
                    attack_id=attack_id,
                    model_name=model_name,
                    response=llm_response,
                    latency=time.time() - start_time
                )
                
                # 5) Output Guardrails & Agent Phase
                output_blocked = self._run_output_phase(llm_response, record)
                if not output_blocked:
                    agent_blocked = self._run_agent_phase(llm_response, record)
                    output_blocked = agent_blocked
                    
                if output_blocked:
                    # 6) Failure Detection & Learning
                    self.ade.learn_from_failure(
                        prompt=prompt,
                        response=llm_response,
                        attack_type=attack_type,
                        risk_score=max(record.get("input_risk", 0), record.get("output_risk", 0)),
                        guardrails_triggered=[record["guardrail_name"]]
                    )
                    self.db.log_defense_memory(
                        embedding=None,
                        attack_type=attack_type,
                        action="BLOCK",
                        confidence=1.0,
                        from_attack_id=attack_id
                    )
                else:
                    record["final_response"] = llm_response

        record["response_time"] = time.time() - start_time
        
        # --- DATABASE LOGGING ---
        self.db.log_attack(
            attack_id=attack_id, prompt=prompt, attack_type=attack_type, 
            source="pipeline", embedding=None
        )
        
        self.db.log_guardrail_result(
            attack_id=attack_id,
            rebuff=record["guardrail_name"] == "Rebuff (Injection Detector)",
            presidio=record["guardrail_name"] == "Presidio (PII Filter)",
            judge=record["guardrail_name"] == "GroqLLMJudge",
            similarity=record["guardrail_name"] == "AdaptiveDefenseEngine",
            final_action="BLOCKED" if record["blocked"] else "ALLOWED",
            risk=max(record.get("input_risk", 0), record.get("output_risk", 0))
        )
        
        self.db.log_attack_outcome(
            attack_id=attack_id,
            success=not record["blocked"], # True if attack succeeded (bypassed filters)
            category=attack_type,
            defense=record["guardrail_name"] or "None",
            severity="High" if record["blocked"] else "Low"
        )
        # ------------------------

        self.log_result(record)
        return record
