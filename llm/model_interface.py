import os
from dotenv import load_dotenv

# LangChain imports
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class LLMInterface:
    def __init__(self):
        load_dotenv()
        self.groq_key = os.getenv("GROQ_API_KEY")
        
        # Initialize LangChain model
        if self.groq_key:
            self.llm = ChatGroq(
                groq_api_key=self.groq_key,
                model_name="llama-3.1-8b-instant",
                temperature=0.7
            )
            
            # Create a simple LangChain pipeline (Prompt -> LLM -> Output String)
            prompt_template = ChatPromptTemplate.from_template("{input}")
            self.chain = prompt_template | self.llm | StrOutputParser()
        else:
            print("[LLMInterface] Warning: GROQ_API_KEY missing.")
            self.llm = None
            self.chain = None

    def generate_response(self, prompt, model_name="llama-3.1-8b-instant", max_length=500):
        """
        Executes the LangChain pipeline to generate a response.
        """
        try:
            if not self.chain:
                return "Error: LangChain pipeline / GROQ_API_KEY not configured."
                
            # Invoke the LangChain runnable sequence
            response = self.chain.invoke({"input": prompt})
            return response.strip()
            
        except Exception as e:
            return f"Error communicating with LangChain model endpoint: {e}"
