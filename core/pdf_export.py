"""Make PDF files of the summary and the quiz.

Two steps, kept apart on purpose:
1. summary_blocks() / quiz_blocks() decide WHAT goes in the PDF: a list of (style, text) blocks.
2. make_pdf() decides HOW it looks: it draws the blocks with fpdf2.
"""
from pathlib import Path

from core.transcript import format_time

# One font file that has both Latin and Arabic letters. Put DejaVuSans.ttf in the fonts folder.
FONT_PATH = Path(__file__).resolve().parent.parent / "fonts" / "DejaVuSans.ttf"

TEAL, INK, GREY = (15, 118, 110), (20, 32, 43), (90, 104, 117)
GREEN, RED = (22, 101, 52), (180, 35, 24)

# style -> (font size, colour, space after in mm)
STYLES = {
    "title": (18, TEAL, 3),
    "meta": (10, GREY, 5),
    "heading": (12, TEAL, 2),
    "text": (11, INK, 4),
    "bullet": (11, INK, 2),
    "question": (12, INK, 1),
    "option": (11, INK, 0),
    "right": (11, GREEN, 0),  # the correct option
    "wrong": (11, RED, 0),  # the option the student picked, when it was wrong
    "why": (10, GREY, 1),
    "where": (10, GREY, 5),
}


def summary_blocks(video):
    """The summary PDF: title, short summary, key points. Returns [] if the video has no summary."""
    summary = video.get("summary")
    if not summary:
        return []
    blocks = [("title", video["title"]), ("heading", "Summary"), ("text", summary["summary"]), ("heading", "Key points")]
    blocks += [("bullet", f"•  {point}") for point in summary["key_points"]]
    return blocks


def quiz_blocks(video, quiz, result):
    """The quiz PDF: the score, then every question with its options, the right answer, the reason and the time.

    result is what core.grading.grade() returned for quiz["answers"].
    """
    share = round(100 * result["score"] / result["total"])
    blocks = [
        ("title", f"Quiz: {video['title']}"),
        ("meta", f"Score: {result['score']} / {result['total']}  ({share}%)"),
    ]
    for number, (question, picked) in enumerate(zip(quiz["questions"], quiz["answers"]), start=1):
        blocks.append(("question", f"{number}. {question['question']}"))
        for position, option in enumerate(question["options"]):
            text, style = f"{'ABCD'[position]}. {option}", "option"
            if position == question["answer"]:
                text, style = text + ("   ✓ Your answer" if position == picked else "   ✓ Correct answer"), "right"
            elif position == picked:
                text, style = text + "   ✗ Your answer", "wrong"
            blocks.append((style, text))
        if question["explanation"]:
            blocks.append(("why", f"Why: {question['explanation']}"))
        blocks.append(("where", f"Explained in the video at {format_time(question['start'])}"))
    return blocks


def make_pdf(blocks, rtl=False):
    """Draw the blocks on A4 pages and return the PDF as bytes. rtl=True for Arabic (text sits on the right)."""
    from fpdf import FPDF  # imported here so the rest of this file works even where fpdf2 is not installed

    if not FONT_PATH.exists():
        raise FileNotFoundError(f"Font not found: {FONT_PATH}. Put DejaVuSans.ttf in the fonts folder.")

    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font("body", fname=str(FONT_PATH))
    pdf.set_text_shaping(True)  # joins Arabic letters and puts mixed Arabic/English words in the right order
    pdf.add_page()
    for style, text in blocks:
        size, colour, gap = STYLES[style]
        pdf.set_font("body", size=size)
        pdf.set_text_color(*colour)
        pdf.multi_cell(0, size * 0.5 + 2, text, align="R" if rtl else "L", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(gap)
    return bytes(pdf.output())