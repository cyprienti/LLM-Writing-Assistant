#!/usr/bin/env python3
"""
ollama_message.py

Usage:
    python ollama_message.py "Your message here" "Your System prompt here"
"""

import sys, os
from ollama import Client, ChatResponse
model_name = "deepseek-r1:70b"
host_name = "http://nc.hcigroup.de:11434"
system_prompt = """
Long system prompt.
Using Multiple lines of text.
Always end your sentences with ':)'.
"""

# Remove any proxy settings inherited from the environment
for key in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
    os.environ.pop(key, None)

def send_message(model: str, message: str, system_prompt: str) -> str:
    """
    Send a single user message to an Ollama model and return the assistant's reply.
    """
    
    client = Client(
        host=host_name,
    )

    response: ChatResponse = client.chat(
        model=model,
        messages=[
            {"role": "system",
             "content": system_prompt
            },
            {
            "role": "user",
            "content": message,
        }]
    )
    return response.message.content

def main():
    if len(sys.argv) < 2:
        print("Usage: python ollama_message.py \"Your message here\"")
        sys.exit(1)

    user_msg = " ".join(sys.argv[1:])
    reply = send_message(model_name, user_msg, system_prompt)
    print(f"Model reply: {reply}")

if __name__ == "__main__":
    main()
