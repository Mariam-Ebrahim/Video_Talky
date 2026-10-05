import requests

from core.chunker import chunk_transcript
from core.llm_json import BadFormatError
from core.rag import ChunkIndex
from core.sections import make_sections
from core.summary import make_summary
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
    """Fetch, index, split and summarize one video. Raises TranscriptError or LLMError on failure.

    on_step(text) is called before each stage; on_progress(done, total) during the sections stage.
    Returns {"id", "url", "title", "language", "index", "snippets", "sections", "summary"}.
    "summary" is {"summary", "key_points"}, or None if the model could not write it.
    """
    step = on_step or (lambda text: None)
    video_id = get_video_id(url)

    step("Fetching the transcript...")
    transcript = fetch_transcript(video_id)
    step("Building the search index...")
    index = ChunkIndex(chunk_transcript(transcript))
    step("Writing the sections (about a minute)...")
    sections = make_sections(transcript, progress=on_progress)
    step("Writing the summary...")
    try:
        summary = make_summary(sections, transcript["language"])
    except BadFormatError: 
        summary = None

    return {
        "id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": fetch_title(video_id),
        "language": transcript["language"],
        "index": index,
        "snippets": transcript["snippets"], 
        "sections": sections,
        "summary": summary,
    }