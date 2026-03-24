import os
from dotenv import load_dotenv

class LLMInterface:
    def __init__(self):
        load_dotenv()
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.gemini_key = os.getenv("GOOGLE_API_KEY")
        
        # Groq client setup
        if self.groq_key:
            from groq import Groq
            self.groq_client = Groq(api_key=self.groq_key)
        else:
            print("[LLMInterface] Warning: GROQ_API_KEY missing.")
            self.groq_client = None

        # Gemini setup 
        self.gemini_ready = False
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                self.gemini_ready = True
            except ImportError:
                print("[LLMInterface] Missing google-generativeai package.")

        # Local HuggingFace FLAN-T5 fallback setup
        self.local_ready = False
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            import torch
            self.tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.local_model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small").to(self.device)
            self.local_ready = True
        except ImportError:
            print("[LLMInterface] Transformers missing for local evaluation.")

    def generate_response(self, prompt, model_name="llama-3.1-8b-instant", max_length=500):
        try:
            if "gemini" in model_name.lower():
                if not self.gemini_ready: return "Error: Gemini SDK/Key unavailable."
                return self.gemini_model.generate_content(prompt).text.strip()
                
            elif "flan" in model_name.lower() or "local" in model_name.lower():
                if not self.local_ready: return "Error: Transformers/Local model unavailable."
                inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
                outputs = self.local_model.generate(**inputs, max_length=max_length)
                return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
            else: # Default Groq (llama-3.1 / mixtral)
                if not self.groq_client: return "Error: GROQ_API_KEY not configured."
                # Fallback intercept
                model_route = "llama-3.1-8b-instant" if "llama3" in model_name else model_name
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=model_route,
                    temperature=0.7,
                    max_tokens=max_length
                )
                return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            return f"Error communicating with target model endpoint: {e}"
