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


def _post(path, payload, url, token, timeout):
    """POST json to the model server and return the parsed reply. Shared by chat() and chat_batch()."""
    url, token = _settings(url, token)
    try:
        response = requests.post(
            f"{url}{path}",
            headers={
                "Authorization": f"Bearer {token}",
                "ngrok-skip-browser-warning": "true",  # ngrok free plan shows a warning page otherwise
            },
            json=payload,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise LLMError(
            "Cannot reach the model server. Is the Kaggle notebook running, and is the URL current?"
        ) from exc

    if response.status_code == 401:
        raise LLMError("The server rejected the API key.")
    if response.status_code == 503:
        raise LLMError("The model server ran out of GPU memory. Try again.")
    if not response.ok:
        raise LLMError(f"The model server returned an error ({response.status_code}).")
    return response.json()


def chat(messages, max_new_tokens=600, temperature=0.0, url=None, token=None):
    """Send a list of {"role", "content"} messages to the model and return its answer."""
    data = _post(
        "/generate",
        {"messages": messages, "max_new_tokens": max_new_tokens, "temperature": temperature},
        url, token, timeout=300,
    )
    return data["response"]


BATCH_SIZE = 5  # the server accepts at most 10 conversations per call; lower this if the GPU runs out of memory


def chat_batch(conversations, max_new_tokens=600, temperature=0.0, url=None, token=None):
    """Like chat(), but for many conversations at once. Returns a list of answers in the same order.

    The GPU writes all the answers at the same time, which is much faster than one after another.
    """
    answers = []
    for i in range(0, len(conversations), BATCH_SIZE):
        data = _post(
            "/generate_batch",
            {
                "conversations": conversations[i:i + BATCH_SIZE],
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
            },
            url, token, timeout=600,
        )
        answers.extend(data["responses"])
    return answers


def ask(system, user, **options):
    """One-shot helper for tasks without history (sections, summary, quiz)."""
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    return chat(messages, **options)


def ask_batch(system, users, **options):
    """Batch version of ask(): the same system prompt for every text in `users`."""
    conversations = [
        [{"role": "system", "content": system}, {"role": "user", "content": user}]
        for user in users
    ]
    return chat_batch(conversations, **options)


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