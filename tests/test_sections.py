import time

from core.sections import make_sections
from core.transcript import fetch_transcript, format_time, get_video_id

LINKS = {
    "English": "https://www.youtube.com/watch?v=fGVfqA_Iv6s",
    "Arabic": "https://www.youtube.com/watch?v=6iGkHOFpBqk",
}

for name, link in LINKS.items():
    transcript = fetch_transcript(get_video_id(link))
    started = time.time()
    sections = make_sections(transcript, progress=lambda done, total: print(f"  {done}/{total}", end="\r"))
    print(f"\n=== {name}: {len(sections)} sections in {time.time() - started:.0f} seconds")
    for s in sections:
        print(f"{format_time(s['start']):>5}  {s['title']}\n       {s['summary']}")