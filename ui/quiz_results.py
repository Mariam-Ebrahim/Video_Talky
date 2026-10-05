import streamlit as st

from core.grading import earn_badges, grade, is_perfect
from core.pdf_export import quiz_blocks
from core.transcript import format_time
from ui.downloads import pdf_button
from ui.helpers import safe
from ui.state import jump


def _message(score, total):
    """One encouraging line for the grade."""
    share = score / total
    if share == 1:
        return "Perfect score!"
    if share >= 0.8:
        return "Great job! You understood this video very well."
    if share >= 0.5:
        return "Good effort. Check the questions you missed below."
    return "Keep going. Watch the parts shown below and try again."


def _show_score(result, quiz):
    """The big score and one numbered circle per question: green if right, red if wrong."""
    chips = "".join(
        f'<div class="chip {"ok" if right else "bad"}">{number}</div>'
        for number, right in enumerate(result["correct"], start=1)
    )
    share = round(100 * result["score"] / result["total"])
    best = max(quiz["scores"])
    attempts = ""
    if len(quiz["scores"]) > 1:  # only worth showing once there is something to compare
        attempts = f'<div class="score-text">Attempt {len(quiz["scores"])} &middot; best so far {best} / {result["total"]}</div>'
    st.markdown(
        f'<div class="score"><div class="score-num">{result["score"]} / {result["total"]}</div>'
        f'<div class="score-text">{share}% &middot; {_message(result["score"], result["total"])}</div>'
        f'{attempts}<div class="chips">{chips}</div></div>',
        unsafe_allow_html=True,
    )


def _celebrate(result, quiz):
    """Congratulations and badges for a full score. The balloons fly once per attempt, not on every rerun."""
    st.markdown(
        '<div class="congrats"><div class="congrats-title">&#127881; Congratulations!</div>'
        "<div>You answered every question correctly.</div>"
        '<div class="badges">'
        + "".join(
            f'<div class="badge"><div class="badge-icon">{icon}</div><b>{title}</b><span>{sub}</span></div>'
            for icon, title, sub in earn_badges(result, quiz["round"])
        )
        + "</div></div>",
        unsafe_allow_html=True,
    )
    if quiz["celebrated"] != quiz["round"]:
        quiz["celebrated"] = quiz["round"]
        st.balloons()


def _retake(quiz):
    """Same questions again: forget the answers; the new round number gives the radios new, empty keys."""
    quiz["answers"] = None
    quiz["round"] += 1


def _show_actions(video, quiz, new_quiz):
    """Two ways to keep practising: the same questions again, or a different set about the same video."""
    again, other = st.columns(2)
    with again:
        st.button("Retake this quiz", key=f"retake_{video['id']}_{quiz['round']}", on_click=_retake, args=(quiz,),
                  use_container_width=True)
    with other:
        if st.button("Try a different quiz", key=f"newquiz_{video['id']}_{quiz['round']}", type="primary",
                     use_container_width=True):
            if new_quiz():
                st.rerun()


def _review_html(number, question, picked):
    """One question with all four options: the right one in green, a wrong pick in red."""
    options = ""
    for position, option in enumerate(question["options"]):
        css, tag = "opt", ""
        if position == question["answer"]:
            css, tag = "opt right", "Your answer" if position == picked else "Correct answer"
        elif position == picked:
            css, tag = "opt wrong", "Your answer"
        label = f'<span class="opt-tag">{tag}</span>' if tag else ""
        options += f'<div class="{css}" dir="auto">{"ABCD"[position]}. {safe(option)}{label}</div>'
    why = f'<div class="why" dir="auto"><b>Why:</b> {safe(question["explanation"])}</div>' if question["explanation"] else ""
    mark = "&#10003;" if picked == question["answer"] else "&#10007;"
    return (
        f'<div class="question" dir="auto"><span class="qnum">{number} {mark}</span>{safe(question["question"])}</div>'
        f"{options}{why}"
    )


def _show_review(video, quiz, result):
    """Every question with the right answer, the reason, and a button to the moment it is explained."""
    with st.container(height=520, border=False):
        for number, (question, picked) in enumerate(zip(quiz["questions"], quiz["answers"])):
            st.markdown(_review_html(number + 1, question, picked), unsafe_allow_html=True)
            st.button(  # the key starts with "src_", so it gets the same small pill style as the chat sources
                f"▶ {format_time(question['start'])}  where it is explained",
                key=f"src_quiz_{video['id']}_{quiz['round']}_{number}",
                on_click=jump,
                args=(video["id"], question["start"]),
            )


def show_results(video, quiz, new_quiz):
    """The screen after submitting: the grade, a celebration for a full score, the actions, then the review.

    new_quiz: a function that writes a different quiz and returns True on success (it shows its own errors).
    """
    result = grade(quiz["questions"], quiz["answers"])
    if len(quiz["scores"]) < quiz["round"]:  # first time this attempt is shown: remember its score
        quiz["scores"].append(result["score"])
    _show_score(result, quiz)
    if is_perfect(result):
        _celebrate(result, quiz)
    _show_actions(video, quiz, new_quiz)
    pdf_button("Download quiz with answers (PDF)", quiz_blocks(video, quiz, result), video, "quiz",
               key=f"dl_quiz_{video['id']}_{quiz['uid']}_{quiz['round']}")
    _show_review(video, quiz, result)