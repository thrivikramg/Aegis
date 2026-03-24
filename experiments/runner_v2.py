import json
import os
import sys
from tqdm import tqdm

# Root project directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.guardrail_manager import GuardrailManager
from llm.model_interface import LLMInterface

class BenchmarkRunner:
    def __init__(self, dataset_path="attacks/jailbreak_prompts.json"):
        self.manager = GuardrailManager()
        self.llm = LLMInterface()
        self.dataset_path = dataset_path

    def run_benchmark(self):
        """Iterates through category-based attacks and evaluates guardrails."""
        if not os.path.exists(self.dataset_path):
            print(f"Error: Dataset {self.dataset_path} not found.")
            return

        with open(self.dataset_path, 'r') as f:
            attacks = json.load(f)

        print("[STARTING] SentinelLLM V2 Benchmark suite...")
        for category, prompts in attacks.items():
            print(f"\nEvaluating Category: [{category.upper()}]")
            for prompt in tqdm(prompts, desc=f"Testing {category}"):
                self.manager.run_full_pipeline(
                    prompt=prompt,
                    llm_interface=self.llm,
                    model_name="flan-t5-small",
                    attack_type=category
                )
        
        print("\n[COMPLETED] Benchmark completed. Results saved to experiments/results_v2.csv")

if __name__ == "__main__":
    runner = BenchmarkRunner()
    runner.run_benchmark()
