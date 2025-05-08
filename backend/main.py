import json
from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
# Add CORS if you call from React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def ollama_generate(model: str, prompt: str, temperature=0.7, stream: bool=False) -> str:
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "stream": False
    })
    return response.json()["response"]

class PromptRequest(BaseModel):
    title: str
    prompt: str

@app.post("/api/complete")
def complete(req: PromptRequest):
    prompt = (
        "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n"
        "The user is writing lyrics for a song. "
        "If the last line is incomplete, complete it. "
        "If it's complete, write the next line. But don't write more than that."
        "Stay in the same lyrical and emotional tone and don't be corny. "
        "Write like a sensate using concrete details and avoid clichés. "
        "Be fun. Don't talk about hearts and souls and stuff unless the "
        "song is already doing that. Just respond with lyrics, don't explain "
        "what you've done.  Assume the last line is incomplete unless the lyrics end on a new line.\n\n"
        f"Title: {req.title.strip() or '(Untitled)'}\n\n"
        f"Lyrics:\n{req.prompt}\n"
        "<|start_header_id|>assistant<|end_header_id|>\n"
    )
    print(prompt)
    response = ollama_generate("llama3:instruct", prompt, temperature=0.7)
    result = response.json()
    return {"completion": result["response"]}

class SubstitutionRange(BaseModel):
    start: int
    end: int

class RewriteReq(BaseModel):
    lyrics: str            # highlighted fragment
    range: SubstitutionRange            # entire current line (optional but helps)
    style: str | None    # “Bob Dylan”, “modern pop”, etc.

@app.post("/api/rewrite")
def rewrite(req: RewriteReq):
    lyrics_with_marker = (
        req.lyrics[:req.range.start] + "«SEL»" + req.lyrics[req.range.end:]
    )
    prompt = (
    "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n"
        f"You are rewriting song lyrics in the style of {req.style or "Bob Dylan"}.\n"
        "In the text below, the token «SEL» marks the exact fragment the user selected.\n"
        "Provide exactly THREE distinct rewrite options that could replace «SEL»,\n"
        "keeping the rhyme scheme and rhythm of the surrounding lines.\n"
        "Return ONLY a JSON array of strings, no extra words. Your full response "
        "must be a valid JSON string.\n"
        "Example format (do NOT include this line):\n"
        "[\"alt 1\",\"alt 2\",\"alt 3\"]\n\n"
        "Full song:\n"
        f"{lyrics_with_marker}\n"
        "<|start_header_id|>assistant<|end_header_id|>\n"
    )
    print(prompt)
    resp = ollama_generate("llama3:instruct", prompt, temperature=0.9)
    print(resp)
    return json.loads(resp)  # → ["Alt 1", "Alt 2", "Alt 3"]