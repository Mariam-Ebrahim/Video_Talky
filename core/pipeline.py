import requests

from core.chunker import chunk_transcript
from core.rag import ChunkIndex
from core.sections import make_sections
from core.transcript import fetch_transcript, get_video_id


def fetch_title(video_id):
    """The video title from YouTube's public oEmbed endpoint (no key needed)."""
    try:
        reply = requests.get(
            "https://www.youtube.com/oembed",
            params={"url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"},
            timeout=8,
        )
        reply.raise_for_status()
        return reply.json()["title"]
    except Exception:
        return f"Video {video_id}"


def process_video(url, on_step=None, on_progress=None):
    """Fetch, index and split one video. Raises TranscriptError or LLMError on failure.

    on_step(text) is called before each stage; on_progress(done, total) during the sections stage.
    Returns {"id", "url", "title", "language", "index", "sections"}.
    """
    step = on_step or (lambda text: None)
    video_id = get_video_id(url)

    step("Fetching the transcript...")
    transcript = fetch_transcript(video_id)
    step("Building the search index...")
    index = ChunkIndex(chunk_transcript(transcript))
    step("Writing the sections (about a minute)...")
    sections = make_sections(transcript, progress=on_progress)

    return {
        "id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": fetch_title(video_id),
        "language": transcript["language"],
        "index": index,
        "sections": sections,
    }