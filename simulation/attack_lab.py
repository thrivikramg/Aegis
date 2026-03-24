import os
import sys
import datetime
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.guardrail_manager import GuardrailManager
from llm.model_interface import LLMInterface
from core.database import Database

class AttackLab:
    """Systematic batch inferencer prioritizing continuous background testing of newly minted AI mutations."""
    def __init__(self):
        self.manager = GuardrailManager()
        self.llm = LLMInterface()
        self.db = Database()

    def simulate_campaign(self, model="llama-3.1-8b-instant", limit=50):
        if not self.db.enabled: return
        
        print(f"[Attack Lab] Initializing deep simulation campaign vs target bounds [{model}]...")
        
        # Pull untried mutations and AI-generated hypotheses 
        muts = list(self.db.mutated_attacks.find({"tested": {"$ne": True}}).limit(limit))
        gens = list(self.db.generated_attacks.find({"evaluation_result": "pending"}).limit(limit))
        
        prompts = [(m["_id"], m.get("mutated_prompt", ""), "mutation") for m in muts] + \
                  [(g["_id"], g.get("generated_prompt", ""), "generated") for g in gens]
                  
        if not prompts:
            print("[Attack Lab] Zero unchecked conceptual attacks sitting in the queue.")
            return
            
        print(f"[Attack Lab] Evaluating {len(prompts)} autonomous payloads sequentially...")
        
        for p_id, prompt, p_type in tqdm(prompts, desc="Executing Campaign Sandbox"):
            res = self.manager.run_full_pipeline(
                prompt=prompt,
                llm_interface=self.llm,
                model_name=model,
                attack_type=f"sim_v5_{p_type}"
            )
            
            # Log exact evaluation natively to V5 simulation arrays
            self.db._async_run(
                self.db.attack_simulation_results.insert_one, {
                    "attack_id": str(p_id),
                    "model_name": model,
                    "success": not res["blocked"],
                    "latency": res["response_time"],
                    "tokens_used": len(prompt.split()) + 50, # Rough heuristic representation
                    "risk_score": res["risk_score"],
                    "timestamp": datetime.datetime.now()
                }
            )
            
            # Formally flush queue targets
            if p_type == "mutation":
                self.db._async_run(self.db.mutated_attacks.update_one, {"_id": p_id}, {"$set": {"tested": True}})
            else:
                self.db._async_run(self.db.generated_attacks.update_one, {"_id": p_id}, {"$set": {"evaluation_result": "tested"}})
                
        print("[Attack Lab] Live Campaign natively concluded.")
        
if __name__ == "__main__":
    lab = AttackLab()
    lab.simulate_campaign()
