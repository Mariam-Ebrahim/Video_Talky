import re

from core.chunker import make_chunks
from core.text_utils import normalize_arabic
from core.transcript import fetch_transcript, get_video_id

LINK = "https://www.youtube.com/watch?v=6iGkHOFpBqk"  # your Arabic video
QUESTIONS = [
    "ما وظيفة اللوحة الأم؟",
    "ما هي ذاكرة الوصول العشوائي؟",
    "ما الفرق بين القرص الصلب والاس اس دي؟",
    "ما هو كرت الشاشة؟",
    "ما هي أنواع التبريد؟",
]


def words(text):
    return re.findall(r"\w+", text)


chunks = make_chunks(fetch_transcript(get_video_id(LINK))["snippets"], 20, 12)
transcript_words = set(words(" ".join(c["text"] for c in chunks)))
normalized_words = {normalize_arabic(w) for w in transcript_words}

print("First chunk, before and after:")
print(chunks[0]["text"][:90])
print(normalize_arabic(chunks[0]["text"])[:90])
print()

for q in QUESTIONS:
    q_words = words(q)
    raw = sum(w in transcript_words for w in q_words)
    norm = sum(normalize_arabic(w) in normalized_words for w in q_words)
    print(q)
    print(f"   question words found in the transcript: raw {raw}/{len(q_words)} -> normalized {norm}/{len(q_words)}")