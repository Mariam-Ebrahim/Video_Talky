from core.grading import grade

QUESTIONS = [{"answer": 0}, {"answer": 2}, {"answer": 3}]

assert grade(QUESTIONS, [0, 2, 3]) == {"score": 3, "total": 3, "correct": [True, True, True]}
assert grade(QUESTIONS, [1, 2, 0]) == {"score": 1, "total": 3, "correct": [False, True, False]}
assert grade(QUESTIONS, [3, 3, 2])["score"] == 0
print("grading OK")
from core.grading import earn_badges, is_perfect

PERFECT = grade(QUESTIONS, [0, 2, 3])
MISSED = grade(QUESTIONS, [1, 2, 3])
assert is_perfect(PERFECT) and not is_perfect(MISSED)
assert not is_perfect(grade([], []))  # an empty quiz is never "perfect"
assert earn_badges(MISSED, 1) == []  # no badges without a full score
assert [b[1] for b in earn_badges(PERFECT, 1)] == ["Perfect score", "First try"]
assert [b[1] for b in earn_badges(PERFECT, 3)] == ["Perfect score", "Never gave up"]
print("badges OK")