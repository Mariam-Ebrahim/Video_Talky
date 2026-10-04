import os

import requests
from dotenv import load_dotenv

load_dotenv()  

class LLMError(Exception):
    """The model server could not give an answer. The message is safe to show to the user."""


def _settings(url, token):
    """Use the given values, or fall back to .env. The ngrok URL changes on every restart."""
    url = (url or os.getenv("LLM_URL") or "").rstrip("/")
    token = token or os.getenv("LLM_TOKEN") or ""
    if not url or not token:
        raise LLMError("The server URL or API key is missing. Check your .env file.")
    return url, token


def chat(messages, max_new_tokens=600, temperature=0.0, url=None, token=None):
    """Send a list of {"role", "content"} messages to the model and return its answer."""
    url, token = _settings(url, token)
    try:
        response = requests.post(
            f"{url}/generate",
            headers={
                "Authorization": f"Bearer {token}",
                "ngrok-skip-browser-warning": "true",  # ngrok free plan shows a warning page otherwise
            },
            json={
                "messages": messages,
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
            },
            timeout=300,
        )
    except requests.RequestException as exc:
        raise LLMError(
            "Cannot reach the model server. Is the Kaggle notebook running, and is the URL current?"
        ) from exc

    if response.status_code == 401:
        raise LLMError("The server rejected the API key.")
    if not response.ok:
        raise LLMError(f"The model server returned an error ({response.status_code}).")
    return response.json()["response"]


def ask(system, user, **options):
    """One-shot helper for tasks without history (sections, summary, quiz)."""
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return chat(messages, **options)


def is_online(url=None):
    """True if the server answers /health. Lets the UI show an online/offline badge."""
    try:
        url = (url or os.getenv("LLM_URL") or "").rstrip("/")
        response = requests.get(
            f"{url}/health", headers={"ngrok-skip-browser-warning": "true"}, timeout=10
        )
        return response.ok
    except requests.RequestException:
        return False