from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.guardrail_manager import GuardrailManager
from llm.model_interface import LLMInterface
import uvicorn
import os

app = FastAPI(title="SentinelLLM API Server", version="2.0")

# Pre-initialized models
manager = GuardrailManager()
llm = LLMInterface()

class AttackRequest(BaseModel):
    prompt: str
    attack_type: str = "generic"
    model_name: str = "flan-t5-small"

@app.post("/v1/analyze", responses={500: {"description": "Internal Server Error during guardrail processing"}})
async def analyze_attack(request: AttackRequest):
    """
    Main endpoint for analyzing an adversarial prompt through 
    the full guardrail pipeline.
    """
    try:
        result = manager.run_full_pipeline(
            prompt=request.prompt,
            llm_interface=llm,
            model_name=request.model_name,
            attack_type=request.attack_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
