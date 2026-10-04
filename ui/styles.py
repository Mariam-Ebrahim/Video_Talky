import streamlit as st

ACCENT = "#0F766E"

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
html, body, .stApp, .stMarkdown, button, input, textarea {{ font-family: 'DM Sans', sans-serif !important; }}
.block-container {{ padding-top: 4.5rem; max-width: 1280px; }}
[data-testid="stForm"] {{ border: 0; padding: 0; }}

/* shared */
.brand {{ font-weight: 700; font-size: 20px; color: {ACCENT}; }}
.label {{ font-size: 13px; color: #5A6875; font-weight: 700; letter-spacing: .04em; margin: 8px 0 6px; }}

/* home */
.topbar {{ display: flex; justify-content: space-between; align-items: center; padding: 0 0 8px; }}
.nav {{ display: flex; gap: 28px; font-size: 15px; color: #3B4A57; }}
.hero {{ text-align: center; padding-top: 4vh; }}
.hero-title {{ font-size: 56px; line-height: 1.1; font-weight: 700; margin-bottom: 16px; }}
.hero-text {{ font-size: 19px; color: #3B4A57; max-width: 620px; margin: 0 auto 28px; }}
.cards {{ display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; margin-top: 40px; }}
.card {{ width: 200px; padding: 20px; background: #fff; border-radius: 14px; border: 1px solid #DDE4EA; }}
.card b {{ display: block; margin-bottom: 6px; }}
.card span {{ font-size: 14px; color: #3B4A57; }}

/* workspace */
.title {{ font-size: 22px; font-weight: 700; padding-bottom: 8px; }}

/* sections list and sidebar videos: buttons that look like rows */
[class*="st-key-sec_"] .stButton, [class*="st-key-secA_"] .stButton,
[class*="st-key-vid_"] .stButton, [class*="st-key-active_"] .stButton {{ width: 100%; }}
[class*="st-key-sec_"] button, [class*="st-key-secA_"] button,
[class*="st-key-vid_"] button, [class*="st-key-active_"] button {{
    width: 100%; justify-content: flex-start; text-align: left; border: 0; border-radius: 8px;
    background: transparent; box-shadow: none; font-size: 14px; padding: 8px 12px; }}
[class*="st-key-secA_"] button, [class*="st-key-active_"] button {{ background: #E3F1EF; font-weight: 500; }}
[class*="st-key-sec_"] button:hover, [class*="st-key-vid_"] button:hover {{ background: #EEF3F6; }}
/* chat */
.bubble {{ max-width: 85%; padding: 12px 16px; border-radius: 14px; margin: 8px 0 4px; font-size: 15px; line-height: 1.55; }}
.bubble.user {{ background: {ACCENT}; color: #fff; margin-left: auto; }}
.bubble.assistant {{ background: #F1F4F6; color: #14202B; margin-right: auto; }}
[class*="st-key-src_"] button {{ min-height: 0; padding: 2px 12px; border: 1px solid #E4B98C; border-radius: 99px;
    background: #fff; color: #B45309; font-size: 13px; font-weight: 700; }}
</style>
"""


def apply_styles():
    """Inject the app's CSS. Call once per run, right after set_page_config."""
    st.markdown(_CSS, unsafe_allow_html=True)