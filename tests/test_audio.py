"""Send one audio file to the Kaggle server's /transcribe endpoint.

Run from the project folder:  py -m tests.test_audio path\\to\\audio.m4a
The server URL and API key come from your .env file (LLM_URL, LLM_TOKEN), never from this file.
"""
import sys

import requests

from core.llm_client import _settings

if len(sys.argv) != 2:
    sys.exit("Usage: py -m tests.test_audio path\\to\\audio.m4a")

url, token = _settings(None, None)

with open(sys.argv[1], "rb") as f:
    r = requests.post(
        f"{url}/transcribe",
        headers={"Authorization": f"Bearer {token}", "ngrok-skip-browser-warning": "true"},
        files={"file": f},
        timeout=900,
    )

print(r.status_code)
if not r.ok:
    sys.exit(r.text)  # show the real server error instead of a JSON decode failure
data = r.json()
print(data["language"], data["segments"][:3])