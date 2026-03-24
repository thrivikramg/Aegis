from core.guardrail_base import BaseGuardrail

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    HAS_PRESIDIO = True
except ImportError:
    HAS_PRESIDIO = False

class PresidioFilter(BaseGuardrail):
    def __init__(self):
        super().__init__(name="Microsoft Presidio (PII Filter)")
        if HAS_PRESIDIO:
            print("Initializing Presidio Analyzer...")
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()
        else:
            print("Presidio not found. Falling back to simple regex for PII.")
            import re
            self.email_pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
            
    def validate(self, text, **kwargs):
        """Detects and redacts PII."""
        if HAS_PRESIDIO:
            results = self.analyzer.analyze(text=text, language='en')
            # If PII is found, we anonymize and report as a "soft" block or warning
            # Depending on research goal, we can either block or just flag.
            # Here we flag if PII exists.
            found_pii = len(results) > 0
            if found_pii:
                redacted = self.anonymizer.anonymize(text=text, analyzer_results=results)
                reason = f"PII detected. Redacted: {redacted.text[:50]}..."
                return False, 0.8, reason # We don't necessarily block, just flag/redact
            return False, 0.0, "Safe"
        else:
            # Fallback regex
            emails = self.email_pattern.findall(text)
            if emails:
                return False, 0.5, f"Email(s) detected: {emails}"
            return False, 0.0, "Safe"

if __name__ == "__main__":
    filter = PresidioFilter()
    print(filter.run("My name is John Doe and my email is john@example.com"))
