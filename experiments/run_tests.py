import sys
import os
import pandas as pd
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm.model_interface import LLMInterface
from redteam.attack_generator import AttackGenerator
from guardrails.prompt_filter import PromptFilter
from guardrails.output_filter import OutputFilter
from evaluation.metrics import MetricsEngine

class ExperimentRunner:
    def __init__(self):
        self.llm = LLMInterface()
        self.attacks = AttackGenerator()
        self.prompt_filter = PromptFilter()
        self.output_filter = OutputFilter()

    def run_benchmark(self, num_prompts_per_category=15):
        categories = ["prompt_injection", "jailbreak", "harmful_instructions", "data_leakage"]
        results = []

        print(f"Starting experiment with {len(categories)} categories...")

        for category in categories:
            prompts = self.attacks.get_attack_prompts(category)
            # Ensure we have enough prompts by mutating if needed
            while len(prompts) < num_prompts_per_category:
                prompts.append(self.attacks.mutate_prompt(random.choice(prompts)))
            
            # Limit to num_prompts_per_category
            prompts = prompts[:num_prompts_per_category]

            for prompt in tqdm(prompts, desc=f"Testing {category}"):
                # 1. Run WITHOUT guardrails
                response_no_guard = self.llm.generate_response(prompt)
                
                # 2. Run WITH guardrails
                prompt_blocked, prompt_reason = self.prompt_filter.is_blocked(prompt)
                
                response_with_guard = ""
                response_blocked = False
                res_reason = "Safe"
                risk_score = 0.0

                if not prompt_blocked:
                    response_with_guard = self.llm.generate_response(prompt)
                    response_blocked, risk_score, res_reason = self.output_filter.is_blocked(response_with_guard)
                else:
                    response_with_guard = "[BLOCKED BY PROMPT FILTER]"
                
                results.append({
                    "attack_type": category,
                    "prompt": prompt,
                    "response_no_guard": response_no_guard,
                    "response_with_guard": response_with_guard,
                    "prompt_blocked": prompt_blocked,
                    "response_blocked": response_blocked,
                    "risk_score": risk_score,
                    "reason": prompt_reason if prompt_blocked else res_reason
                })

        df = pd.DataFrame(results)
        df.to_csv("experiments/results.csv", index=False)
        print("Experiment completed. Results saved to experiments/results.csv")
        return df

if __name__ == "__main__":
    import random # needed for mutation logic in dummy benchmark
    runner = ExperimentRunner()
    runner.run_benchmark(num_prompts_per_category=13) # Total 52 prompts
