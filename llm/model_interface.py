from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

class LLMInterface:
    def __init__(self, model_name="google/flan-t5-small"):
        print(f"Loading model {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        # Check for CUDA and specify device mapping to avoid meta-tensor issues
        device_map = "auto" if torch.cuda.is_available() else None
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name, 
            device_map=device_map,
            low_cpu_mem_usage=True
        )
        self.device = self.model.device

    def generate_response(self, prompt, max_length=100):
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(**inputs, max_length=max_length)
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

if __name__ == "__main__":
    llm = LLMInterface()
    test_prompt = "Explain quantum physics in one sentence."
    print(f"Prompt: {test_prompt}")
    print(f"Response: {llm.generate_response(test_prompt)}")
