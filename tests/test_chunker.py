from core.transcript import get_video_id, fetch_transcript
from core.chunker import make_chunks

vid = get_video_id("https://www.youtube.com/watch?v=fGVfqA_Iv6s")
t = fetch_transcript(vid)
chunks = make_chunks(t["snippets"])

words = [len(c["text"].split()) for c in chunks]
print("chunks:", len(chunks))
print("words per chunk: average", sum(words) // len(words), "max", max(words))
print(chunks[0])
print(chunks[1])
print("last end:", chunks[-1]["end"], "video duration:", t["duration"])