import html


def safe(text):
    """Escape text for HTML. '$' is escaped too, so Streamlit does not read it as a formula."""
    return html.escape(text).replace("\n", "<br>").replace("$", "&#36;")