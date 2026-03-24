from abc import ABC, abstractmethod
import time

class BaseGuardrail(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def validate(self, input_text, **kwargs):
        """
        Validates the text. 
        Returns (is_blocked, score, reason)
        """
        pass

    def run(self, text, **kwargs):
        start_time = time.time()
        is_blocked, score, reason = self.validate(text, **kwargs)
        duration = time.time() - start_time
        return {
            "guardrail_name": self.name,
            "blocked": is_blocked,
            "risk_score": score,
            "reason": reason,
            "latency": duration
        }
