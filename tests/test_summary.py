import time

from core.sections import make_sections
from core.summary import make_summary
from core.transcript import fetch_transcript, get_video_id

LINKS = {
    "English": "https://www.youtube.com/watch?v=fGVfqA_Iv6s",
    "Arabic": "https://www.youtube.com/watch?v=ICYP77MU5K0",
}

for name, link in LINKS.items():
    transcript = fetch_transcript(get_video_id(link))
    sections = make_sections(transcript)  # about 45 seconds: the summary is built from these notes
    started = time.time()
    result = make_summary(sections, transcript["language"])
    print(f"\n=== {name}: summary in {time.time() - started:.0f} seconds\n")
    print(result["summary"])
    print()
    for point in result["key_points"]:
        print(f" - {point}")