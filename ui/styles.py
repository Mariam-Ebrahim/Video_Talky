import streamlit as st

ACCENT = "#0F766E"

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');
  html, body, .stApp, .stMarkdown, button, input, textarea {{ font-family: 'DM Sans', sans-serif !important; }} 
.block-container {{ padding-top: 4.5rem; max-width: 1280px; }}
[data-testid="stForm"] {{ border: 0; padding: 0; }}

/* top bar */
.topbar {{ display: flex; justify-content: space-between; align-items: center; padding: 0 0 8px; }}
.brand {{ font-weight: 700; font-size: 20px; color: {ACCENT}; }}
.nav {{ display: flex; gap: 28px; font-size: 15px; color: #3B4A57; }}

/* home hero */
.hero {{ text-align: center; padding-top: 4vh; }}
.hero-title {{ font-size: 56px; line-height: 1.1; font-weight: 700; margin-bottom: 16px; }}
.hero-text {{ font-size: 19px; color: #3B4A57; max-width: 620px; margin: 0 auto 28px; }}

/* feature cards */
.cards {{ display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; margin-top: 40px; }}
.card {{ width: 200px; padding: 20px; background: #fff; border-radius: 14px; border: 1px solid #DDE4EA; }}
.card b {{ display: block; margin-bottom: 6px; }}
.card span {{ font-size: 14px; color: #3B4A57; }}
</style>
"""


def apply_styles():
    """Inject the app's CSS. Call once per run, right after set_page_config."""
    st.markdown(_CSS, unsafe_allow_html=True)