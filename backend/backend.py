from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, Dict
import requests
import uvicorn
import logging
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
"""
LLM Writing Assistant Backend

This FastAPI application serves as the backend for the LLM Writing Assistant.
It provides an endpoint that simulates LLM-based text improvements and corrections.

Students are expected to expand this template by:
1. Implementing actual Ollama integration
2. Enhancing the text processing logic
3. Adding additional endpoints as needed
"""

app = FastAPI(title="LLM Writing Assistant API")

# Allow CORS for integration with the Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AssistRequest(BaseModel):
    text: str
    mode: Literal["full", "grammar"] = "full"

# Main endpoint
@app.post("/assist")
async def assist_report(data: AssistRequest) -> Dict[str, str]:
    """
    Improves or corrects input text using a local LLaMA 3 model via Ollama.
    """
    original_text = data.text.strip()
    if not original_text:
        raise HTTPException(status_code=422, detail="Empty text input.")

    # Prepare prompt
    if data.mode == "grammar":
        prompt = (
            "Correct the grammar, spelling, and punctuation in the following text. "
            "Do **not** change the style, tone, vocabulary, structure, or meaning. "
            "Respond with **only** the corrected text.\n\n"
            f"{original_text}"
        )
    else:
        prompt = (
            "Improve the clarity, style and academic tone of the following text. "
            "Do **not** change the meaning and the language. "
            "Respond with the corrected text **only**.\n\n"
            f"{original_text}"
        )

    # Query Ollama
    try:
        logging.info(f"Sending request to LLaMA 3 (mode={data.mode})")
        response = query_ollama(prompt)
        return {"assisted_text": response.strip()}
    except Exception as e:
        logging.exception("LLM error")
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

# Internal function to query Ollama
def query_ollama(prompt: str, model: str = "llama3") -> str:
    """
    Sends a prompt to the local Ollama server and returns the model response.
    """
    res = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=90  # seconds
    )
    res.raise_for_status()
    return res.json()["response"]

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": await request.body()},
    )

# Entry point
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
