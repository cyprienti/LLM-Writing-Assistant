import requests
from typing import Literal
from pydantic import BaseModel

API_URL = "http://127.0.0.1:8000/assist"


class AssistRequest(BaseModel):
    text: str
    mode: Literal["full", "grammar"] = "full"


def correct_text(input_text: str, mode: Literal["full", "grammar"]) -> str:
    request_body = AssistRequest(text=input_text, mode=mode)

    response = requests.post(API_URL, json=request_body.dict())
    response.raise_for_status()

    return response.json()["assisted_text"]
