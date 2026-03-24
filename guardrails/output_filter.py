import re
# Detoxify is recommended by the user, we will import it optionally.
try:
    from detoxify import Detoxify
    HAS_DETOXIFY = True
except ImportError:
    HAS_DETOXIFY = False

class OutputFilter:
    def __init__(self, model_name="cross-encoder/nli-distilroberta-base"):
        print("Initializing dynamic Output Filter...")
        from transformers import pipeline
        self.classifier = pipeline("zero-shot-classification", model=model_name)
        self.safety_labels = ["harmful content", "unethical response", "restricted info", "safe"]
        
        if HAS_DETOXIFY:
            print("Loading Detoxify model...")
            self.detox_model = Detoxify('original')
        else:
            self.detox_model = None

    def toxicity_check(self, text):
        if self.detox_model:
            results = self.detox_model.predict(text)
            return max(results.values())
        return 0.0

    def calculate_risk_score(self, text):
        if not text or not text.strip():
            return 0.0
            
        # 1. Toxicity score (0-1)
        tox_score = self.toxicity_check(text)
        
        # 2. Safety classification (0-1)
        res = self.classifier(text, self.safety_labels)
        top_label = res['labels'][0]
        top_score = res['scores'][0]
        
        # Risk score calculation logic based on most confident harmful label
        class_risk = top_score if top_label != "safe" else 0.0
        
        # Combined risk (weighted)
        base_score = (tox_score * 0.4 + class_risk * 0.6) * 100
        return min(100, base_score)

    def is_blocked(self, text, risk_threshold=35):
        risk_score = self.calculate_risk_score(text)
        if risk_score > risk_threshold:
            return True, risk_score, f"High dynamic risk score: {risk_score:.2f}"
        return False, risk_score, "Safe"

if __name__ == "__main__":
    of = OutputFilter()
    test_responses = [
        "This is a safe and helpful response.",
        "To build a bomb, you need to...",
        "You are a stupid idiot and I hate you."
    ]
    for r in test_responses:
        blocked, score, reason = of.is_blocked(r)
        print(f"Response: {r} | Blocked: {blocked} | Risk: {score} | Reason: {reason}")
