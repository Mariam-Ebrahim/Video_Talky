import streamlit as st

from core.chat import ask_video
from core.llm_client import LLMError
from core.transcript import format_time
from ui.helpers import safe
from ui.state import jump


def show_bubble(role, text):
    """One chat message. dir="auto" lets the browser align Arabic right-to-left and English left-to-right."""
    st.markdown(f'<div class="bubble {role}" dir="auto">{safe(text)}</div>', unsafe_allow_html=True)


def show_sources(video, sources, number):
    """Small time buttons under an answer. A click moves the player to that time."""
    if not sources:
        return
    columns = st.columns([1] * len(sources) + [max(8 - len(sources), 1)])
    for i, (column, source) in enumerate(zip(columns, sources)):
        column.button(
            f"\u25b6 {format_time(source['start'])}",
            key=f"src_{video['id']}_{number}_{i}",
            on_click=jump,
            args=(video["id"], source["start"]),
        )


def show_chat(video):
    """The Chat tab: the conversation of this video, and a box to ask the next question."""
    box = st.container(height=520, border=False)  # the messages scroll inside this box
    question = st.chat_input("Ask about this video...")

    with box:
        if not video["messages"] and not question:
            st.caption("Ask anything about this video. Answers come only from its transcript.")
        for number, message in enumerate(video["messages"]):
            show_bubble(message["role"], message["content"])
            if message["role"] == "assistant":
                show_sources(video, message["sources"], number)

        if question:
            show_bubble("user", question)
            try:
                with st.spinner("Thinking..."):
                    result = ask_video(question, video["index"], video["history"])
            except LLMError as exc:  # their messages are written for the user; nothing is saved
                st.error(str(exc))
                return
            video["messages"].append({"role": "user", "content": question})
            video["messages"].append(
                {"role": "assistant", "content": result["answer"], "sources": result["sources"]}
            )
    if question:
        st.rerun()  # draw the saved conversation again, with working source buttons