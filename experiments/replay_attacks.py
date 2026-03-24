import os
import sys
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.guardrail_manager import GuardrailManager
from llm.model_interface import LLMInterface
from core.database import Database

class ReplayTester:
    """Script identifying zero-day historical bypasses and routing them to re-test the updated Aegis."""
    def __init__(self):
        self.manager = GuardrailManager()
        self.llm = LLMInterface()
        self.db = Database()

    def run_replay(self, model="llama-3.1-8b-instant"):
        print("[STARTING] Aegis V5 Adaptive Defense Replay Tester...")
        if not self.db.enabled:
            print("Database not enabled. Cannot execute deep-memory replays.")
            return
            
        # Fetch historically successful attacks (vulns that bypassed the pipeline completely)
        cursor = self.db.attacks.find({"success": True})
        docs = list(cursor)
        unique_prompts = set([d["attack_prompt"] for d in docs if "attack_prompt" in d])
        
        if not unique_prompts:
            print("No vulnerabilities to test. The defense grid is unpenetrated.")
            return
            
        print(f"Discovered {len(unique_prompts)} unique past vulnerability patterns.")
        print(f"Replaying them maliciously against the V3 system...")
        
        blocked_count = 0
        for prompt in tqdm(unique_prompts, desc="Replaying Vulnerabilities"):
            res = self.manager.run_full_pipeline(
                prompt=prompt,
                llm_interface=self.llm,
                model_name=model,
                attack_type="historic_replay"
            )
            
            if res["blocked"]:
                blocked_count += 1
            
            # Log exact evaluation diagnostics internally
            self.db._async_run(
                self.db.defense_evaluation.insert_one, {
                    "replayed_prompt": prompt,
                    "target_model": model,
                    "successfully_blocked_on_replay": res["blocked"],
                    "caught_by": res["guardrail_name"]
                }
            )
            
        rate = (blocked_count / len(unique_prompts)) * 100
        print(f"\n[REPORT] Zero-Day Retrospective Replay Assesment:")
        print(f"Total Exploits Tested: {len(unique_prompts)}")
        print(f"Caught by Adapted Defense: {blocked_count}")
        print(f"Net Defense Efficacy Growth: {rate:.1f}%")

if __name__ == "__main__":
    tester = ReplayTester()
    tester.run_replay()
