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
        Executes the entire guardrail pipeline.
        Returns the final response and a summary of the security decisions.
        """
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
            "output_risk": 0.0
        }
        
        start_time = time.time()
        
        if not self._run_input_phase(prompt, record):
            llm_response = llm_interface.generate_response(prompt)
            
            if not self._run_output_phase(llm_response, record):
                if not self._run_agent_phase(llm_response, record):
                    record["final_response"] = llm_response

        record["response_time"] = time.time() - start_time
        self.log_result(record)
        return record
