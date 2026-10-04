import streamlit as st

from core.transcript import format_time
from ui.home import show_home
from ui.state import current_video, init_state, new_video, process_and_open
from ui.styles import apply_styles

st.set_page_config(page_title="VidTalk", page_icon="🎬", layout="wide")
apply_styles()
init_state()

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
    # TEMPORARY check view: it proves the pipeline works. Step 3 replaces it with the workspace.
    st.button("Back to home", on_click=new_video)
    st.subheader(video["title"])
    for s in video["sections"]:
        st.write(f"**{format_time(s['start'])}** {s['title']}: {s['summary']}")