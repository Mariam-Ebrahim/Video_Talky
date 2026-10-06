import os
import shutil
import tempfile
import threading
import time
from pathlib import Path
from typing import Literal

import torch
import uvicorn
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from pydantic import BaseModel, Field
from pyngrok import ngrok
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline,
)


def secret(name: str) -> str:
    try:
        from kaggle_secrets import UserSecretsClient

        return UserSecretsClient().get_secret(name)
    except Exception:
        return os.environ[name]


MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")
API_KEY = secret("API_KEY")

# --- LLM: loaded in 4-bit (~5 GB instead of ~15 GB) so Whisper fits on the same GPU ---
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME, quantization_config=bnb_config, device_map={"": 0}
)

# --- Whisper ---
asr = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-medium",
    dtype=torch.float16,
    device="cuda:0",
)

app = FastAPI(title="Video Talky LLM server")
lock = threading.Lock()  # one GPU job at a time (chat OR transcription)


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

    try:
        with lock:
            with torch.inference_mode():
                output = model.generate(**inputs, **gen_kwargs)
    except torch.OutOfMemoryError:
        torch.cuda.empty_cache()
        raise HTTPException(status_code=503, detail="GPU out of memory, input too long")
    finally:
        torch.cuda.empty_cache()

    new_tokens = output[0][inputs["input_ids"].shape[1]:]
    return {"response": tokenizer.decode(new_tokens, skip_special_tokens=True)}
    
class BatchRequest(BaseModel):
    conversations: list[list[Message]] = Field(min_length=1, max_length=10)
    max_new_tokens: int = Field(600, ge=1, le=2048)
    temperature: float = Field(0.0, ge=0.0, le=1.5)


@app.post("/generate_batch")
def generate_batch(request: BatchRequest, authorization: str = Header(default="")):
    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    texts = [
        tokenizer.apply_chat_template(
            [m.model_dump() for m in conv], add_generation_prompt=True, tokenize=False
        )
        for conv in request.conversations
    ]
    tokenizer.padding_side = "left"  # decoder models must pad on the left when batching
    inputs = tokenizer(texts, return_tensors="pt", padding=True).to(model.device)

    gen_kwargs = {"max_new_tokens": request.max_new_tokens, "pad_token_id": tokenizer.eos_token_id}
    if request.temperature > 0:
        gen_kwargs.update(do_sample=True, temperature=request.temperature, top_p=0.9)
    else:
        gen_kwargs.update(do_sample=False)

    try:
        with lock:
            with torch.inference_mode():
                output = model.generate(**inputs, **gen_kwargs)
    except torch.OutOfMemoryError:
        torch.cuda.empty_cache()
        raise HTTPException(status_code=503, detail="GPU out of memory, input too long")
    finally:
        torch.cuda.empty_cache()

    prompt_len = inputs["input_ids"].shape[1]
    return {
        "responses": [
            tokenizer.decode(row[prompt_len:], skip_special_tokens=True) for row in output
        ]
    }

@app.post("/transcribe")
def transcribe(file: UploadFile = File(...), authorization: str = Header(default="")):
    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    suffix = Path(file.filename or "").suffix or ".m4a"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)  # save the uploaded audio to disk

    try:
        with lock:
            result = asr(
                tmp.name,
                chunk_length_s=30,
                batch_size=4,  # smaller batch = less GPU memory
                return_timestamps=True,
                generate_kwargs={"num_beams": 1},  # greedy decoding, no beam-search memory blowup
            )
    except torch.OutOfMemoryError:
        torch.cuda.empty_cache()
        raise HTTPException(status_code=503, detail="GPU out of memory during transcription")
    finally:
        os.remove(tmp.name)
        torch.cuda.empty_cache()

    segments = []
    for chunk in result["chunks"]:
        start, end = chunk["timestamp"]
        end = end if end is not None else start + 5  # the last chunk can have no end
        segments.append({"text": chunk["text"].strip(), "start": start, "duration": end - start})

    text = " ".join(s["text"] for s in segments)
    arabic = sum("\u0600" <= ch <= "\u06FF" for ch in text)
    language = "ar" if arabic > len(text) * 0.3 else "en"  # simple guess from the letters
    return {"language": language, "segments": segments}


if __name__ == "__main__":
    threading.Thread(
        target=uvicorn.run,
        args=(app,),
        kwargs={"host": "0.0.0.0", "port": 8000, "log_level": "warning"},
        daemon=True,
    ).start()
    ngrok.set_auth_token(secret("NGROK_TOKEN"))
    print("PUBLIC URL:", ngrok.connect(8000).public_url)
    while True:
        time.sleep(60)