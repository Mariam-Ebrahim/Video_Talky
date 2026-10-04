from sentence_transformers import SentenceTransformer

from core.chunker import make_chunks
from core.transcript import fetch_transcript, get_video_id

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
VIDEOS = {
    "English": "https://www.youtube.com/watch?v=fGVfqA_Iv6s",
    "Arabic": "https://www.youtube.com/watch?v=6iGkHOFpBqk",
}
SETTINGS = [(15, 10), (20, 12), (20, 15), (30, 20), (45, 30)]  # (window, stride) in seconds

model = SentenceTransformer(MODEL_NAME)
limit = model.max_seq_length
print("model limit:", limit, "tokens\n")


def count_tokens(text):
    return len(model.tokenizer(text, truncation=False)["input_ids"])  # includes the special tokens


for name, link in VIDEOS.items():
    transcript = fetch_transcript(get_video_id(link))
    snippets = transcript["snippets"]
    all_text = " ".join(s["text"] for s in snippets)
    ratio = count_tokens(all_text) / len(all_text.split())
    print(f"=== {name}: {len(snippets)} snippets, {ratio:.2f} tokens per word")
    print("window stride | chunks | words avg/max | tokens avg/max | over the limit")
    for window, stride in SETTINGS:
        chunks = make_chunks(snippets, window, stride)
        words = [len(c["text"].split()) for c in chunks]
        tokens = [count_tokens(c["text"]) for c in chunks]
        over = sum(t > limit for t in tokens)
        print(
            f"{window:>6} {stride:>6} | {len(chunks):>6} | "
            f"{sum(words) // len(words):>4}/{max(words):<4}    | "
            f"{sum(tokens) // len(tokens):>5}/{max(tokens):<5}    | "
            f"{over} of {len(chunks)} ({100 * over // len(chunks)}%)"
        )
    print()