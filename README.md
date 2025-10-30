# LLM-Writing-Assistant
A local AI-powered writing assistant built with **FastAPI**, **Streamlit**, and **LLaMA 3 (via Ollama)**.  
This app helps users improve their writing by offering two modes:
-  Grammar Correction
-  Full Revision (clarity, tone, structure)

---

##  Features

-  Accepts user input in natural language (e.g. seminar text)
-  Sends prompts to a local LLaMA 3 model via **Ollama**
-  Receives and displays improved text
-  Shows side-by-side **diff viewer** (word-level changes)
-  Copy to clipboard and export results as `.txt`

---

##  Tech Stack

| Layer      | Tool                     |
|------------|--------------------------|
| Frontend   | Streamlit                |
| Backend    | FastAPI                  |
| Model      | LLaMA 3 via Ollama       |
| Diff Logic | `difflib`, `re`, `HTML`  |

---

##  Getting Started

### 1.  Start your LLaMA3 model locally via Ollama

```bash
ollama run llama3
```

### 2.  Run the backend (FastAPI)
```bash
uvicorn backend:app --reload
```
### 3.  Run the frontend (Streamlit)
```bash
streamlit run frontend.py
```
