import requests
from core.timing import timed
from core.audio import download_audio
from core.llm_client import LLMError, _settings
from core.transcript import TranscriptError


def transcribe_video(video_id):
    """Download the audio, send it to the Kaggle Whisper server, and return a transcript
    in the same format as fetch_transcript()."""
    with timed("download audio"):
        audio_path = download_audio(video_id)
    url, token = _settings(None, None)
    try:
        with timed("upload + whisper"):
            with open(audio_path, "rb") as audio:
                reply = requests.post(
                    f"{url}/transcribe",
                    headers={"Authorization": f"Bearer {token}", "ngrok-skip-browser-warning": "true"},
                    files={"file": audio},
                    timeout=1800,  
                )
    except requests.RequestException as exc:
        raise LLMError("Cannot reach the model server. Is the Kaggle notebook running?") from exc
    finally:
        audio_path.unlink(missing_ok=True) 

    if reply.status_code == 401:
        raise LLMError("The server rejected the API key.")
    if reply.status_code == 503:
        raise LLMError("The model server ran out of GPU memory. Try again, or use a shorter video.")
    if not reply.ok:
        raise LLMError(f"The transcription failed on the server ({reply.status_code}).")

    data = reply.json()
    snippets = [
        {"text": s["text"], "start": float(s["start"]), "duration": float(s["duration"])}
        for s in data["segments"]
        if s["text"].strip()
    ]
    if not snippets:
        raise TranscriptError("No speech was found in this video.")

    last = snippets[-1]
    return {
        "video_id": video_id,
        "language": data["language"],
        "is_generated": True,
        "source": "whisper",
        "duration": last["start"] + last["duration"],
        "snippets": snippets,
    }