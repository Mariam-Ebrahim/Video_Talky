from core.chunker import make_chunks
from core.rag import ChunkIndex
from core.transcript import fetch_transcript, format_time, get_video_id

SETTINGS = [(15, 10), (20, 12), (30, 20)]  # (window, stride) in seconds
DETAIL_SETTING = (20, 12)                  # print the details only for this one
TOP_K = 3
MIN_OVERLAP = 5                            # seconds a result must share with the answer to count as a hit

# (question, answer starts at, answer ends at) in seconds. Check them against your transcripts
# and add your own questions.
VIDEOS = {
    "English": {
        "link": "https://www.youtube.com/watch?v=fGVfqA_Iv6s",
        "questions": [
            ("What does the CPU do?", 30, 70),
            ("Why is RAM not storage?", 120, 135),
            ("What is the difference between SSD and HDD?", 160, 210),
            ("What is the GPU?", 212, 272),
            ("What does the PSU do?", 323, 372),
            ("What is thermal throttling?", 376, 391),
            ("What is a bottleneck?", 479, 519),
        ],
    },
    "Arabic": {
        "link": "https://www.youtube.com/watch?v=6iGkHOFpBqk",
        "questions": [
            ("ما وظيفة اللوحة الأم؟", 1, 45),
            ("ما هو المعالج؟", 45, 90),
            ("ما هي الرام؟", 90, 131),
            ("ما الفرق بين الاس اس دي والقرص الصلب؟", 179, 205),
            ("ما هو كرت الشاشة؟", 207, 246),
            ("ما وظيفة مزود الطاقة؟", 246, 277),
            ("ما أنواع التبريد؟", 304, 331),
        ],
    },
}


def overlap(chunk, start, end):
    """How many seconds the chunk shares with the answer's time range."""
    return min(chunk["end"], end) - max(chunk["start"], start)


results_table = {}
for name, video in VIDEOS.items():
    snippets = fetch_transcript(get_video_id(video["link"]))["snippets"]
    for window, stride in SETTINGS:
        index = ChunkIndex(make_chunks(snippets, window, stride))
        hits = 0
        for question, start, end in video["questions"]:
            found = index.search(question, k=TOP_K)
            hit = any(overlap(c, start, end) >= MIN_OVERLAP for c in found)
            hits += hit
            if (window, stride) == DETAIL_SETTING:
                print(f"[{name}] {question}   (answer at {format_time(start)}-{format_time(end)})  ->  "
                      f"{'HIT' if hit else 'MISS'}")
                for c in found:
                    print(f"    {format_time(c['start']):>5}-{format_time(c['end']):<5} "
                          f"score {c['score']:.2f}  {c['text'][:60]}")
        results_table[(name, window, stride)] = (hits, len(video["questions"]))

print(f"\nHits in the top {TOP_K} results")
print("window stride |", " | ".join(f"{n:^9}" for n in VIDEOS))
for window, stride in SETTINGS:
    row = [f"{results_table[(n, window, stride)][0]}/{results_table[(n, window, stride)][1]}" for n in VIDEOS]
    print(f"{window:>6} {stride:>6} |", " | ".join(f"{r:^9}" for r in row))