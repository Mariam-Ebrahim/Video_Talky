import streamlit as st

from core.llm_client import LLMError
from core.similar import find_similar
from core.transcript import format_time
from ui.helpers import safe


def _forget(video):
    video["similar"] = None  # lets the user search again


def show_similar(video):
    """The Similar tab: videos on the same topic. The search runs only when the user asks for it."""
    result = video.get("similar")

    if result is None:
        st.caption("Find more videos on the same topic.")
        if st.button("Find similar videos", key=f"similar_{video['id']}", type="primary"):
            with st.spinner("Searching YouTube..."):
                try:
                    video["similar"] = find_similar(video["title"], video["sections"], video["language"], video["id"])
                except LLMError as exc:  # its message is written for the user
                    st.error(str(exc))
                    return
            st.rerun()
        return

    if not result["videos"]:
        st.info("No similar videos were found. YouTube may be busy; try again in a moment.")
        st.button("Try again", key=f"retry_{video['id']}", on_click=_forget, args=(video,))
        return

    st.caption("Searched for: " + " \u00b7 ".join(result["keywords"]))
    for item in result["videos"]:
        duration = format_time(item["duration"]) if item["duration"] else ""
        meta = " \u00b7 ".join(part for part in (item["channel"], duration) if part)
        st.markdown(
            f'<div class="similar">'
            f'<a class="similar-title" href="{safe(item["url"])}" target="_blank" rel="noopener" dir="auto">{safe(item["title"])}</a>'
            f'<div class="similar-meta" dir="auto">{safe(meta)}</div></div>',
            unsafe_allow_html=True,
        )