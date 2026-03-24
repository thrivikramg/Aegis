import os
from dotenv import load_dotenv
from groq import Groq

class AttackClassifier:
    """
    Zero-shot LLM classifier running independently of the generation target to 
    dynamically categorize incoming threats.
    """
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        
    def classify(self, prompt: str) -> dict:
        if not self.client:
            return {"attack_type": "unknown", "classification_confidence": 0.0}
            
        sys_prompt = """Classify the user input into exactly one of these labels:
- prompt_injection
- jailbreak_roleplay
- rag_injection
- persona_hijacking
- data_exfiltration
- benign

Return ONLY the label string. No punctuation or introductory text."""
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.0,
                max_tokens=15
            )
            cat = chat_completion.choices[0].message.content.strip().lower()
            valid = ["prompt_injection", "jailbreak_roleplay", "rag_injection", "persona_hijacking", "data_exfiltration", "benign"]
            
            # Simulated confidence calculation
            conf = 0.95 if cat in valid else 0.4
            final_cat = cat if cat in valid else "unknown"
            
            # Severity mapping mapping requested by Dynamic Risk Formulator
            severities = {
                "prompt_injection": 0.8,
                "jailbreak_roleplay": 0.9,
                "rag_injection": 0.85,
                "persona_hijacking": 0.7,
                "data_exfiltration": 1.0,
                "benign": 0.0,
                "unknown": 0.5
            }
            
            return {
                "attack_type": final_cat, 
                "classification_confidence": conf,
                "severity": severities.get(final_cat, 0.5)
            }
        except Exception:
            return {"attack_type": "unknown", "classification_confidence": 0.0, "severity": 0.5}
