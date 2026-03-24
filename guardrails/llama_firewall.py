from core.guardrail_base import BaseGuardrail
import re

class LlamaFirewall(BaseGuardrail):
    def __init__(self):
        super().__init__(name="LlamaFirewall (Agent & Tool Safety)")
        # Danger list for tool execution
        self.dangerous_calls = [
            r"rm\s+-rf",
            r"os\.remove",
            r"subprocess\.run",
            r"eval\(",
            r"exec\(",
            r"curl\s+http",
            r"wget\s+http",
            r"sh\s+[\/\w\.-]+"
        ]
        self.dangerous_patterns = [re.compile(p, re.IGNORECASE) for p in self.dangerous_calls]

    def validate(self, text, **kwargs):
        """Scans for unauthorized or risky tool execution commands."""
        for pattern in self.dangerous_patterns:
            match = pattern.search(text)
            if match:
                return True, 1.0, f"Risky agent command detected: {match.group(0)}"
        return False, 0.0, "Safe"

if __name__ == "__main__":
    fw = LlamaFirewall()
    print(fw.run("To delete your system files, run: rm -rf /"))
