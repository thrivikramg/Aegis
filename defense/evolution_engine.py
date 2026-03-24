import os
import sys
import datetime
from dotenv import load_dotenv
from groq import Groq

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.database import Database
from guardrails.adaptive_defense import AdaptiveDefenseGuardrail

class EvolutionEngine:
    """Tracks successful bypass events and deductively patches architectural logic continuously."""
    def __init__(self, db=None):
        load_dotenv()
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.db = db or Database()
        self.adaptive_guard = AdaptiveDefenseGuardrail()

    def evolve_defenses(self):
        if not self.db.enabled or not self.client: return
        print("[Evolution Engine] Scanning central telemetry for unmitigated penetration events...")
        
        bypasses = list(self.db.attacks.find({"success": True}).sort("timestamp", -1).limit(5))
        
        if not bypasses:
            return
            
        print(f"[Evolution Engine] Interrogating {len(bypasses)} exposed dimensional vulnerabilities. Compiling abstractions...")
        
        for b in bypasses:
            prompt = b.get("attack_prompt", "")
            attack_type = b.get("attack_type", "unknown")
            orig_id = b.get("attack_id", "")
            
            # Utilize an LLM abstractor to formalize the attack mechanic directly
            req = f"Identify the core deceptive framework traversing this prompt: '{prompt}'. Output an ultra-concise heuristic keyword pattern encoding this technique's logic. Absolute maximum 15 words."
            
            try:
                comp = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": req}],
                    model="llama-3.1-8b-instant",
                    temperature=0.2, # Low temp logic deduction
                    max_tokens=50
                )
                pattern_desc = comp.choices[0].message.content.strip()
                
                # Instantiating the deduced logic formally into the framework rule stream 
                self.db._async_run(
                    self.db.defense_rules.insert_one, {
                        "rule_type": "heuristic_heuristic_block",
                        "attack_pattern": pattern_desc,
                        "derived_from": orig_id,
                        "timestamp": datetime.datetime.now(),
                        "confidence": 0.95
                    }
                )
                
                # Formalize immediate spatial blockade inside defense_memory natively
                embedding = self.adaptive_guard.encode(prompt)
                self.db.log_defense_memory({
                    "pattern_embedding": embedding,
                    "attack_type": attack_type,
                    "recommended_action": "BLOCK",
                    "confidence": 1.0, 
                    "created_from_attack": f"rule_evo_{orig_id}"
                })
                
            except Exception as e:
                pass
                
        print("[Evolution Engine] Defense matrix recalibrated securely.")

if __name__ == "__main__":
    evo = EvolutionEngine()
    evo.evolve_defenses()
