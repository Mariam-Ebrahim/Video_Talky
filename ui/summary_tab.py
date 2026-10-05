import streamlit as st

from core.pdf_export import summary_blocks
from ui.downloads import pdf_button
from ui.helpers import safe


def show_summary(video):
    """The Summary tab: a short overview and the key points. Arabic videos are shown right-to-left."""
    summary = video.get("summary")
    if not summary:
        st.info("A summary could not be written for this video.")
        return
    direction = "rtl" if video["language"] == "ar" else "ltr"
    points = "".join(f"<li>{safe(point)}</li>" for point in summary["key_points"])
    st.markdown(
        f'<div class="summary" dir="{direction}">'
        f'<div class="label">SUMMARY</div><p>{safe(summary["summary"])}</p>'
        f'<div class="label">KEY POINTS</div><ul>{points}</ul></div>',
        unsafe_allow_html=True,
    )
    pdf_button("Download summary (PDF)", summary_blocks(video), video, "summary", key=f"dl_summary_{video['id']}")