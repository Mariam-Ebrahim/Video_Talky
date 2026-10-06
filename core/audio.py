import tempfile
from pathlib import Path

import yt_dlp

from core.transcript import TranscriptError

MAX_MINUTES = 180 


def download_audio(video_id):
    """Download only the audio of a YouTube video. Returns the file path."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    folder = Path(tempfile.mkdtemp())
    options = {
        "format": "bestaudio[ext=m4a]/bestaudio", 
        "outtmpl": str(folder / f"{video_id}.%(ext)s"),
        "quiet": True,
        "noplaylist": True,
        "no_warnings": True,
        "remote_components": ["ejs:github"],
    }
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False) 
            if (info.get("duration") or 0) > MAX_MINUTES * 60:
                raise TranscriptError(f"This video is longer than {MAX_MINUTES} minutes.")
            ydl.download([url])
    except yt_dlp.utils.DownloadError as exc:
        raise TranscriptError("Could not download the audio of this video.") from exc
    return next(folder.glob(f"{video_id}.*"))