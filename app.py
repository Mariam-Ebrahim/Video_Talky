import streamlit as st

from ui.home import show_home
from ui.sidebar import show_sidebar
from ui.state import current_video, init_state, process_and_open
from ui.styles import apply_styles
from ui.workspace import show_workspace

st.set_page_config(page_title="Video Talky", page_icon="🎬", layout="wide")
apply_styles()
init_state()

if st.session_state.videos:
    show_sidebar()

video = current_video()
if video is None:
    link = show_home()
    if link is None:
        pass  # nothing submitted yet
    elif not link:
        st.warning("Paste a YouTube link first.")
    elif process_and_open(link):
        st.rerun()
else:
    show_workspace(video)