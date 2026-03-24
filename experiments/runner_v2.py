import json
import os
import sys
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.guardrail_manager import GuardrailManager
from llm.model_interface import LLMInterface

class BenchmarkRunner:
    def __init__(self, dataset_path="attacks/jailbreak_prompts.json"):
        self.manager = GuardrailManager()
        self.llm = LLMInterface()
        
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.dataset_path = os.path.join(base_dir, dataset_path) if not os.path.isabs(dataset_path) else dataset_path
        
        # Testing across V3 Multi-Model Safety Matrix
        self.target_models = [
            "llama-3.1-8b-instant",  # Advanced AI
            "gemini-1.5-flash",      # Corporate baseline
            "google/flan-t5-small"   # Naive local framework
        ]

    def run_benchmark(self):
        """Iterates through all category-based attacks across multiple autonomous targets."""
        if not os.path.exists(self.dataset_path):
            print(f"Error: Dataset {self.dataset_path} not found.")
            return

        with open(self.dataset_path, 'r') as f:
            attacks = json.load(f)

        print("[STARTING] Aegis V5 Multi-Model Benchmark suite...")
        for category, prompts in attacks.items():
            for target_model in self.target_models:
                print(f"\nEvaluating Category: [{category.upper()}] against LLM Target: [{target_model}]")
                for prompt in tqdm(prompts, desc=f"Testing {category} -> {target_model}"):
                    self.manager.run_full_pipeline(
                        prompt=prompt,
                        llm_interface=self.llm,
                        model_name=target_model,
                        attack_type=category
                    )
        
        print("\n[COMPLETED] Benchmark completed. High-fidelity results streaming to Sentinel MongoDB.")

if __name__ == "__main__":
    runner = BenchmarkRunner()
    runner.run_benchmark()
