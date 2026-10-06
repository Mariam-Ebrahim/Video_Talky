import streamlit as st

from core.llm_client import LLMError
from core.quiz import is_educational, make_quiz
from ui.helpers import safe
from ui.quiz_results import show_results
from ui.state import start_generating

LETTERS = "ABCD"
AVOID_LIMIT = 20  # how many earlier questions a new quiz is told to avoid (keeps the prompt short)


def _flag(video):
    """Session key that is True only while a quiz of this video is being written."""
    return f"generating_{video['id']}"


def _error_key(video):
    return f"quiz_error_{video['id']}"


def _start_quiz(video, seen=()):
    """Check the video, write the questions and save the quiz. Returns True on success, False after saving an error.

    seen: the questions of earlier quizzes of this video. A new quiz avoids them. When it is given,
    the video is already known to be educational, so that check is skipped.
    On failure the quiz the user already has is left untouched, and the error message is saved in
    session_state so show_quiz can display it on the next run (the caller always reruns).
    """
    bar = st.progress(0.0, text="Checking the video..." if not seen else "Writing a new quiz...")
    try:
        if not seen and not is_educational(video["title"], video["sections"]):
            video["quiz"] = {"educational": False}
            return True
        bar.progress(0.0, text="Writing all 10 questions (about 50 seconds)...")
        questions = make_quiz(
            video["sections"],
            video["snippets"],
            video["language"],
            avoid=list(seen)[-AVOID_LIMIT:],
)
    except LLMError as exc:  # its message is written for the user
        st.session_state[_error_key(video)] = str(exc)
        return False
    if not questions:
        st.session_state[_error_key(video)] = "The questions could not be written this time. Please try again."
        return False
    # answers stays None until the user submits; round changes on every new attempt so the radios start empty.
    # seen: every question text shown so far. scores: the score of each finished attempt of this quiz.
    # celebrated: the round whose balloons were already shown (a rerun must not repeat them).
    video["quiz"] = {
        "educational": True,
        "questions": questions,
        "answers": None,
        "round": 1,
        "uid": len(seen),  # differs for every quiz of this video, so widget keys are never reused across quizzes
        "seen": [*seen, *(q["question"] for q in questions)],
        "scores": [],
        "celebrated": None,
    }
    return True


def _new_quiz(video, quiz):
    """Called by the 'Try a different quiz' button (via show_results): writes a different quiz."""
    return _start_quiz(video, seen=quiz["seen"])


def _option_label(question, position):
    """'A. text' for one option. '$' is escaped so Streamlit does not read it as a formula."""
    return f"{LETTERS[position]}. {question['options'][position]}".replace("$", "\\$")


def _show_form(video, quiz):
    """All the questions, with no answers shown. Nothing is graded until the user submits every question."""
    key = f"{video['id']}_{quiz['uid']}_{quiz['round']}"
    with st.form(f"quiz_form_{key}", border=False):
        picks = []
        with st.container(height=520, border=False):  # the questions scroll, the Submit button stays visible
            for number, question in enumerate(quiz["questions"]):
                st.markdown(
                    f'<div class="question" dir="auto"><span class="qnum">{number + 1}</span>{safe(question["question"])}</div>',
                    unsafe_allow_html=True,
                )
                picks.append(
                    st.radio(
                        f"Question {number + 1}",
                        range(len(LETTERS)),
                        index=None,
                        format_func=lambda position, q=question: _option_label(q, position),
                        key=f"quiz_{key}_{number}",
                        label_visibility="collapsed",
                    )
                )
        submitted = st.form_submit_button("Submit quiz", type="primary")

    if submitted:
        if None in picks:
            st.warning(f"Please answer every question. {picks.count(None)} left.")
        else:
            quiz["answers"] = picks  # position of the option chosen for each question
            st.rerun()


def show_quiz(video):
    """The Quiz tab. The quiz is written only when the user asks for it."""
    error = st.session_state.pop(_error_key(video), None)  # an error saved by the run that just failed
    if error:
        st.error(error)

    quiz = video.get("quiz")

    if quiz is None:
        flag = _flag(video)
        st.caption("Test yourself on this video: 10 questions. You see your grade and the answers after you submit.")
        # The click sets the flag in a callback, which runs before the script body. So on this run the
        # button is already drawn disabled, and it stays disabled for the whole generation.
        st.button(
            "Start quiz",
            key=f"start_quiz_{video['id']}",
            type="primary",
            disabled=st.session_state.get(flag, False),
            on_click=start_generating,
            args=(flag,),
        )
        if st.session_state.get(flag):
            try:
                _start_quiz(video)
            finally:
                st.session_state[flag] = False  # always release the button, even on error or interruption
            st.rerun()  # success: show the quiz. Failure: redraw with the button enabled and the error shown.
        return

    if not quiz["educational"]:
        st.info("This video does not look educational, so a quiz would not make sense for it.")
        return

    if quiz["answers"] is None:
        _show_form(video, quiz)
        return

    show_results(video, quiz, new_quiz=lambda: _new_quiz(video, quiz))