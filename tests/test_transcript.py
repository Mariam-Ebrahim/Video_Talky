from core.transcript import get_video_id, fetch_transcript, format_time, TranscriptError
links = [
    "https://www.youtube.com/watch?v=xnyFYiK2rSY&t=2s",
    "https://www.youtube.com/watch?v=mvZHDpCHphk",
    "https://www.youtube.com/watch?v=aaaaaaaaaaa",
]


for link in links:
    try:
        video_id = get_video_id(link)
        t = fetch_transcript(video_id)
        print(t["language"], "generated:", t["is_generated"], "snippets:", len(t["snippets"]),
              "length:", format_time(t["duration"]))
        print(t["snippets"][:2])
    except TranscriptError as e:
        print("ERROR:", e)