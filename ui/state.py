import streamlit as st

from core.llm_client import LLMError
from core.pipeline import process_video
from core.transcript import TranscriptError, get_video_id


def init_state():
    """Create the app's session state on the first run."""
    st.session_state.setdefault("videos", {})  # video id -> everything the app knows about that video
    st.session_state.setdefault("current", None)  # id of the open video, or None for the home page


def current_video():
    return st.session_state.videos.get(st.session_state.current)


def new_video():
    st.session_state.current = None


def open_video(video_id):
    st.session_state.current = video_id


def jump(video_id, seconds):
    """Move the player of a video to a time (used by the sections list and the chat sources)."""
    video = st.session_state.videos[video_id]
    video["start"] = int(seconds)
    video["autoplay"] = True


def process_and_open(url):
    """Process a link (unless already done) and open it. Returns True on success, False after showing an error."""
    state = st.session_state
    try:
        video_id = get_video_id(url)
        if video_id not in state.videos:
            with st.status("Processing the video...", expanded=True) as status:
                bar = st.progress(0.0)
                video = process_video(
                    url,
                    on_step=st.write,
                    on_progress=lambda done, total: bar.progress(done / total),
                )
                status.update(label="Done", state="complete", expanded=False)
            # fields the screens will use in the next steps
            state.videos[video_id] = {**video, "start": 0, "autoplay": False, "history": [], "messages": []}
        state.current = video_id
    except (TranscriptError, LLMError) as exc:  # their messages are written for the user
        st.error(str(exc))
        return False
    except Exception as exc:
        st.error(f"Something went wrong: {exc}")
        return False
    return True

def start_generating(flag):
    st.session_state[flag] = True