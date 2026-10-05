import re

import streamlit as st

from core.pdf_export import make_pdf


def file_name(title, kind):
    """'What are Loops? | Kodable' + 'summary' -> 'What are Loops Kodable - summary.pdf' (no characters Windows rejects)."""
    clean = re.sub(r"[^\w\- ]", "", title).strip()[:50] or "video"
    return f"{clean} - {kind}.pdf"


def pdf_button(label, blocks, video, kind, key):
    """A Download button for a PDF. If the PDF cannot be made, show a short message instead of crashing the tab."""
    try:
        data = make_pdf(blocks, rtl=video["language"] == "ar")
    except Exception as exc:
        st.caption(f"The PDF could not be made: {exc}")
        return
    st.download_button(label, data=data, file_name=file_name(video["title"], kind), mime="application/pdf", key=key)