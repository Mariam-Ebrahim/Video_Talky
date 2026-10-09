import re
from contextlib import contextmanager

import requests
from youtube_transcript_api import (
    AgeRestricted,
    CouldNotRetrieveTranscript,
    InvalidVideoId,
    IpBlocked,
    RequestBlocked,
    TranscriptsDisabled,
    VideoUnavailable,
    VideoUnplayable,
    YouTubeTranscriptApi,
)

LANGUAGES = ("ar", "en")  # supported languages, in order of preference
_VIDEO_ID = re.compile(r"(?:[?&]v=|youtu\.be/|shorts/|embed/|live/)([A-Za-z0-9_-]{11})")


class TranscriptError(Exception):
    """The transcript could not be fetched. The message is safe to show to the user."""


class NoCaptionsError(TranscriptError):
    """The video has no usable captions, so the app can fall back to speech recognition."""


def get_video_id(url):
    """Return the 11-character video ID from a YouTube link (or from a bare ID)."""
    url = (url or "").strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url
    match = _VIDEO_ID.search(url)
    if not match or not ("youtube.com" in url or "youtu.be" in url):
        raise TranscriptError("This is not a valid YouTube link.")
    return match.group(1)


def _language(track):
    return track.language_code.split("-")[0]  # "en-US" -> "en"


def _sorted_tracks(transcript_list):
    """Arabic/English caption tracks, best first."""
    found = [t for t in transcript_list if _language(t) in LANGUAGES]
    if not found:
        raise NoCaptionsError("This video has no Arabic or English captions.")
    # auto-generated captions follow the spoken language, so they tell us what is spoken
    spoken = next((_language(t) for t in found if t.is_generated), None)
    return sorted(found, key=lambda t: (_language(t) != spoken, t.is_generated, LANGUAGES.index(_language(t))))


@contextmanager
def _friendly_errors():
    """Turn the library's exceptions into TranscriptError messages for the user."""
    try:
        yield
    except TranscriptsDisabled as exc:
        raise NoCaptionsError("Captions are turned off for this video.") from exc
    except (VideoUnavailable, InvalidVideoId, AgeRestricted, VideoUnplayable) as exc:
        raise TranscriptError("This video is unavailable, private, or restricted.") from exc
    except (RequestBlocked, IpBlocked, requests.RequestException) as exc:
        raise TranscriptError("Could not reach YouTube. Check your connection and try again.") from exc
    except CouldNotRetrieveTranscript as exc:
        raise TranscriptError("Could not get the captions for this video.") from exc



def fetch_transcript(video_id):
    """Fetch the captions of the best Arabic or English track.

    Returns {"video_id", "language", "is_generated", "source", "duration", "snippets"}
    where each snippet is {"text", "start", "duration"} in seconds.
    """
    with _friendly_errors():
        track = _sorted_tracks(YouTubeTranscriptApi().list(video_id))[0]
        fetched = track.fetch()
    snippets = [
        {"text": " ".join(s.text.split()), "start": float(s.start), "duration": float(s.duration)}
        for s in fetched.snippets
        if s.text.strip()
    ]
    if not snippets:
        raise NoCaptionsError("The captions of this video are empty.")
    last = snippets[-1]
    return {
        "video_id": video_id,
        "language": _language(track),
        "is_generated": track.is_generated,
        "source": "captions",
        "duration": last["start"] + last["duration"],
        "snippets": snippets,
    }


def format_time(seconds):
    """83 -> '1:23', 3725 -> '1:02:05'."""
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"