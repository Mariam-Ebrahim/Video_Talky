def grade(questions, answers):
    """Compare the user's picks with the correct options.

    questions: the quiz questions ("answer" is the position of the correct option)
    answers:   the position the user picked for each question
    Returns {"score", "total", "correct"}, where "correct" is a list of True/False, one per question.
    """
    correct = [picked == question["answer"] for question, picked in zip(questions, answers)]
    return {"score": sum(correct), "total": len(questions), "correct": correct}


def is_perfect(result):
    """True when every question was answered correctly."""
    return result["total"] > 0 and result["score"] == result["total"]


def earn_badges(result, attempt):
    """The badges for one attempt: a list of (icon, title, subtitle). Empty unless the score is full.

    attempt: 1 for the first try of this quiz, 2 for the first retake, and so on.
    """
    if not is_perfect(result):
        return []
    badges = [("\U0001F3C6", "Perfect score", f"{result['total']} out of {result['total']}")]
    if attempt == 1:
        badges.append(("⚡", "First try", "No retake needed"))
    else:
        badges.append(("\U0001F4AA", "Never gave up", f"Perfect on attempt {attempt}"))
    return badges