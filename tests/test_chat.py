from core.chat import ask_video
from core.chunker import chunk_transcript
from core.rag import ChunkIndex
from core.transcript import fetch_transcript, format_time, get_video_id

# Each conversation has a follow-up question and one question the video does not answer.
CONVERSATIONS = {
    "English": (
        "https://www.youtube.com/watch?v=fGVfqA_Iv6s",
        ["What does the CPU do?", "And how is it different from the GPU?", "Does the video talk about quantum computers?"],
    ),
    "Arabic": (
        "https://www.youtube.com/watch?v=6iGkHOFpBqk",
        ["ما هي الرام؟", "وما الفرق بينها وبين القرص الصلب؟", "هل يتحدث الفيديو عن الذكاء الاصطناعي؟"],
    ),
}

for name, (link, questions) in CONVERSATIONS.items():
    transcript = fetch_transcript(get_video_id(link))
    index = ChunkIndex(chunk_transcript(transcript))
    history = []  # one chat = one history
    print(f"\n=== {name} ===")
    for question in questions:
        result = ask_video(question, index, history)
        times = " · ".join(format_time(s["start"]) for s in result["sources"])
        best = max(s["score"] for s in result["sources"])
        print(f"\nQ: {question}\nA: {result['answer']}\nSources: {times}   (best score {best:.2f})")
    print(f"\n(history now holds {len(history)} messages)")