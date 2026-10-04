import streamlit as st

from ui.state import new_video, open_video


def show_sidebar():
    """The list of processed videos, with a button to start a new one."""
    with st.sidebar:
        st.markdown('<div class="brand">VidTalk</div>', unsafe_allow_html=True)
        st.button("+ New video", type="primary", use_container_width=True, on_click=new_video)
        st.markdown('<div class="label">YOUR VIDEOS</div>', unsafe_allow_html=True)
        for video_id, video in st.session_state.videos.items():
            prefix = "active" if video_id == st.session_state.current else "vid"
            st.button(video["title"], key=f"{prefix}_{video_id}", on_click=open_video, args=(video_id,))