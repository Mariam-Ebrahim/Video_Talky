import streamlit as st

from core.transcript import format_time
from ui.chat_tab import show_chat
from ui.helpers import safe
from ui.state import jump


def show_player(video):
    try:
        st.video(video["url"], start_time=video["start"], autoplay=video["autoplay"])
    except TypeError:  # older Streamlit versions have no autoplay
        st.video(video["url"], start_time=video["start"])


def show_sections(video):
    """The list of sections. The one the player is in is highlighted; a click jumps the player."""
    st.markdown('<div class="label">SECTIONS</div>', unsafe_allow_html=True)
    sections = video["sections"]
    active = max((i for i, s in enumerate(sections) if s["start"] <= video["start"]), default=0)
    with st.container(border=True):
        for i, section in enumerate(sections):
            prefix = "secA" if i == active else "sec"
            st.button(
                f":orange[**{format_time(section['start'])}**]   {section['title']}",
                key=f"{prefix}_{i}",
                on_click=jump,
                args=(video["id"], section["start"]),
            )


def show_workspace(video):
    st.markdown(f'<div class="title">{safe(video["title"])}</div>', unsafe_allow_html=True)
    left, right = st.columns([4, 6], gap="large")
    with left:
        show_player(video)
        show_sections(video)
    with right:
        chat_tab, summary_tab, quiz_tab, similar_tab = st.tabs(["Chat", "Summary", "Quiz", "Similar"])
        with chat_tab:
            show_chat(video)
        for tab, name in ((summary_tab, "Summary"), (quiz_tab, "Quiz"), (similar_tab, "Similar")):
            with tab:
                st.info(f"The {name} tab comes in a later step.")