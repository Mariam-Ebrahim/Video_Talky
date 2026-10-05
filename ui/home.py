import streamlit as st

FEATURES = [
    ("Summary", "Main points in seconds"),
    ("Sections", "Click a time, jump there"),
    ("Chat", "Ask anything about the video"),
    ("Quiz", "Test yourself, download it"),
    ("Similar videos", "Keep learning the topic"),
]


def show_home():
    """Draw the home page. Returns the link the user submitted, or None."""
    st.markdown(
        '<div class="topbar"><div class="brand">Video Talky</div>'
        '<div class="nav"><span>My videos</span><span>How it works</span></div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero"><div class="hero-title">Talk to any YouTube video</div>'
        '<div class="hero-text">Paste a link. Get a summary, jump-to sections, a quiz, '
        "and answers to your questions.</div></div>",
        unsafe_allow_html=True,
    )

    _, middle, _ = st.columns([1, 4, 1])
    with middle:
        with st.form("link_form"):
            field, button = st.columns([5, 1.6])
            url = field.text_input(
                "YouTube link", placeholder="https://www.youtube.com/watch?v=...", label_visibility="collapsed"
            )
            submitted = button.form_submit_button("Process video", type="primary", use_container_width=True)

    cards = "".join(f'<div class="card"><b>{title}</b><span>{text}</span></div>' for title, text in FEATURES)
    st.markdown(f'<div class="cards">{cards}</div>', unsafe_allow_html=True)

    return url.strip() if submitted else None