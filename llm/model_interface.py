import os
from dotenv import load_dotenv
from groq import Groq

class LLMInterface:
    def __init__(self, model_name="llama-3.1-8b-instant"):
        print(f"Loading Groq model {model_name}...")
        load_dotenv()
        self.api_key = os.getenv("GROQ_API_KEY")
        
        # Fallback to llama3 if an older huggingface name was passed
        if "flan" in model_name or "gpt" in model_name:
            self.model_name = "llama-3.1-8b-instant"
        else:
            self.model_name = model_name
        
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            print("[LLMInterface] Warning: GROQ_API_KEY not found in environment.")
            self.client = None

    def generate_response(self, prompt, max_length=500):
        if not self.client:
            return "Error: GROQ_API_KEY not configured."
            
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model_name,
                temperature=0.7,
                max_tokens=max_length
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            return f"Error communicating with Groq API: {e}"

if __name__ == "__main__":
    llm = LLMInterface()
    test_prompt = "Explain quantum physics in one sentence."
    print(f"Prompt: {test_prompt}")
    print(f"Response: {llm.generate_response(test_prompt)}")
