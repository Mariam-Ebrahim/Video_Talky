def make_chunks(snippets, window, stride):
    """Group caption snippets into overlapping time windows.

    snippets: [{"text", "start", "duration"}, ...] sorted by start time (seconds)
    window:   how many seconds one chunk covers
    stride:   how many seconds to move forward for the next chunk (smaller than window = overlap)
    returns:  [{"id", "text", "start", "end"}, ...]
    """
    if not 0 < stride <= window:
        raise ValueError("stride must be more than 0 and not bigger than window")

    chunks = []
    i = 0  # index of the first snippet of the current chunk
    while i < len(snippets):
        start = snippets[i]["start"]

        # j = first snippet that starts after this chunk's window ends
        j = i
        while j < len(snippets) and snippets[j]["start"] < start + window:
            j += 1

        group = snippets[i:j]
        last = group[-1]
        chunks.append({
            "id": len(chunks),
            "text": " ".join(s["text"] for s in group),
            "start": start,
            "end": last["start"] + last["duration"],
        })

        if j >= len(snippets):  # this chunk reached the end of the video
            break

        # the next chunk starts at the first snippet at or after start + stride
        i += 1
        while snippets[i]["start"] < start + stride:
            i += 1
    return chunks


# (window, stride) in seconds for each language, chosen from the token and retrieval tests
SETTINGS = {"ar": (30, 20), "en": (20, 12)}


def chunk_transcript(transcript):
    """Chunk a transcript dictionary using the settings of its language."""
    window, stride = SETTINGS.get(transcript["language"], SETTINGS["en"])
    return make_chunks(transcript["snippets"], window, stride)