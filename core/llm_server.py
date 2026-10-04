import os
import threading
import time
from typing import Literal

import torch
import uvicorn
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from pyngrok import ngrok
from transformers import AutoModelForCausalLM, AutoTokenizer


def secret(name: str) -> str:
    try:
        from kaggle_secrets import UserSecretsClient

        return UserSecretsClient().get_secret(name)
    except Exception:
        return os.environ[name]


MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")
API_KEY = secret("API_KEY")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME, torch_dtype=torch.float16, device_map="auto"
)

app = FastAPI(title="Video Talky LLM server")
lock = threading.Lock() 

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class GenerateRequest(BaseModel):
    messages: list[Message] = Field(min_length=1)
    max_new_tokens: int = Field(600, ge=1, le=2048)
    temperature: float = Field(0.0, ge=0.0, le=1.5)  


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME}


@app.post("/generate")
def generate(request: GenerateRequest, authorization: str = Header(default="")):
    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    messages = [m.model_dump() for m in request.messages]  
    inputs = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt", return_dict=True
    ).to(model.device)

    gen_kwargs = {
        "max_new_tokens": request.max_new_tokens,
        "pad_token_id": tokenizer.eos_token_id,
    }
    if request.temperature > 0:
        gen_kwargs.update(do_sample=True, temperature=request.temperature, top_p=0.9)
    else:
        gen_kwargs.update(do_sample=False)

    with lock:
        output = model.generate(**inputs, **gen_kwargs)

    new_tokens = output[0][inputs["input_ids"].shape[1]:]  #  only the answer
    return {"response": tokenizer.decode(new_tokens, skip_special_tokens=True)}


if __name__ == "__main__":
    threading.Thread(
        target=uvicorn.run, args=(app,),
        kwargs={"host": "0.0.0.0", "port": 8000, "log_level": "warning"}, daemon=True).start()
    ngrok.set_auth_token(secret("NGROK_TOKEN"))
    print("PUBLIC URL:", ngrok.connect(8000).public_url)
    while True:
        time.sleep(60)