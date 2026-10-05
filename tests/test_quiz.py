import time

from core.pipeline import fetch_title
from core.quiz import is_educational, make_quiz
from core.sections import make_sections
from core.transcript import fetch_transcript, format_time, get_video_id

LINKS = {
    "English": "https://www.youtube.com/watch?v=fGVfqA_Iv6s",
    "Arabic": "https://www.youtube.com/watch?v=6iGkHOFpBqk",
}

for name, link in LINKS.items():
    video_id = get_video_id(link)
    transcript = fetch_transcript(video_id)
    sections = make_sections(transcript)  # about 45 seconds: the quiz follows these sections
    title = fetch_title(video_id)

    print(f"\n=== {name}: {title}")
    print("educational:", is_educational(title, sections))

    started = time.time()
    quiz = make_quiz(sections, transcript["snippets"], transcript["language"],
                     progress=lambda done, total: print(f"  {done}/{total}", end="\r"))
    print(f"{len(quiz)} questions in {time.time() - started:.0f} seconds\n")
    for number, q in enumerate(quiz, start=1):
        print(f"{number}. ({format_time(q['start'])}) {q['question']}")
        for position, option in enumerate(q["options"]):
            print(f"     {'ABCD'[position]}. {option}{'   <-- correct' if position == q['answer'] else ''}")
        print(f"   why: {q['explanation']}\n")