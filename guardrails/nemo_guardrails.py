from core.guardrail_base import BaseGuardrail

try:
    from nemoguardrails import RailsConfig, LLMRails
    HAS_NEMO = True
except ImportError:
    HAS_NEMO = False

class NeMoGuardrails(BaseGuardrail):
    def __init__(self, config_path=None):
        super().__init__(name="NVIDIA NeMo Guardrails")
        if HAS_NEMO and config_path:
            self.config = RailsConfig.from_path(config_path)
            self.rails = LLMRails(self.config)
        else:
            print("NeMo Guardrails not found or config missing. Using policy-based filtering fallback.")
            # We'll mimic a set of policies
            self.forbidden_topics = ["religion", "politics", "medical_advice"]
            
    def validate(self, text, **kwargs):
        """Validates the text against policy and topical clusters."""
        if HAS_NEMO:
            # Full implementation would call self.rails.generate(messages=[{"role": "user", "content": text}])
            # But the validate method is for static checks. 
            # In NeMo, output rails are often computed vs reference.
            # We'll mock a policy violation for demonstration if specific keywords appear.
            pass

        # Lite fallback implementation
        text_lower = text.lower()
        for topic in self.forbidden_topics:
            if topic in text_lower:
                return True, 0.9, f"Policy violation: forbidden topic '{topic}' detected."
        
        return False, 0.0, "Safe"

if __name__ == "__main__":
    nemo = NeMoGuardrails()
    print(nemo.run("I want some medical advice for my flu."))
