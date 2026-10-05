"""PDF export. The content checks need no fpdf2; the sample PDFs are made only if fpdf2 is installed."""
import sys
from unittest.mock import MagicMock

for name in ["youtube_transcript_api", "requests", "dotenv"]:  # only needed to import core.transcript
    try:
        __import__(name)
    except ImportError:
        sys.modules[name] = MagicMock()

from core.grading import grade
from core.pdf_export import make_pdf, quiz_blocks, summary_blocks

SUMMARY = {"summary": "A short overview.", "key_points": ["First point", "Second point"]}
QUIZ = {"questions": [
    {"question": "What is a loop?", "options": ["It repeats", "It stops", "It adds", "It prints"],
     "answer": 0, "explanation": "A loop repeats steps.", "start": 65},
    {"question": "What does SSD mean?", "options": ["a", "b", "c", "d"],
     "answer": 2, "explanation": "", "start": 0},
], "answers": [0, 1]}
RESULT = grade(QUIZ["questions"], QUIZ["answers"])

# --- summary
blocks = summary_blocks({"title": "My video", "summary": SUMMARY})
assert blocks[0] == ("title", "My video")
assert ("bullet", "•  First point") in blocks and ("text", "A short overview.") in blocks
assert summary_blocks({"title": "x", "summary": None}) == []  # no summary -> nothing to download

# --- quiz
blocks = quiz_blocks({"title": "My video"}, QUIZ, RESULT)
assert ("meta", "Score: 1 / 2  (50%)") in blocks
assert ("right", "A. It repeats   ✓ Your answer") in blocks          # picked the right one
assert ("wrong", "B. b   ✗ Your answer") in blocks                   # picked a wrong one
assert ("right", "C. c   ✓ Correct answer") in blocks                # the one they should have picked
assert ("why", "Why: A loop repeats steps.") in blocks
assert ("where", "Explained in the video at 1:05") in blocks
assert [style for style, _ in blocks].count("why") == 1  # the question with no explanation gets no "Why" line
print("pdf content OK")

# --- real PDFs: open them and look, especially the Arabic one
try:
    import fpdf  # noqa: F401
except ImportError:
    print("fpdf2 not installed: skipped the sample PDFs")
else:
    english = make_pdf(blocks + summary_blocks({"title": "My video", "summary": SUMMARY}))
    arabic = make_pdf(
        [("title", "ما هو SSD وما الفرق بينه وبين HDD؟"), ("text", "هذا الفيديو يشرح الفرق بين SSD و HDD و RAM بطريقة بسيطة."),
         ("bullet", "•  القرص SSD أسرع من HDD"), ("right", "أ. الإجابة الصحيحة   ✓")],
        rtl=True,
    )
    assert english.startswith(b"%PDF") and arabic.startswith(b"%PDF")
    open("check_english.pdf", "wb").write(english)
    open("check_arabic.pdf", "wb").write(arabic)
    print("wrote check_english.pdf and check_arabic.pdf: open them. Arabic letters must be joined and read right to left.")