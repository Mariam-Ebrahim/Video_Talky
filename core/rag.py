import faiss
from sentence_transformers import SentenceTransformer

from core.text_utils import normalize_arabic

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"  # understands Arabic and English
_model = None


def _get_model():
    """Load the embedding model once, the first time it is needed."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed(texts):
    """Texts -> unit-length vectors. Arabic spelling is normalized, for searching only."""
    texts = [normalize_arabic(t) for t in texts]
    vectors = _get_model().encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return vectors.astype("float32")  # FAISS needs float32


class ChunkIndex:
    """A searchable index over the chunks of one video."""

    def __init__(self, chunks):
        if not chunks:
            raise ValueError("Cannot build an index without chunks.")
        self.chunks = chunks  # the original chunks: this is what we show to the user
        vectors = embed([c["text"] for c in chunks])
        self.index = faiss.IndexFlatIP(vectors.shape[1])  # inner product on unit vectors = cosine similarity
        self.index.add(vectors)

    def search(self, query, k=4):
        """Return the k most similar chunks, best first, each with a "score" (1.0 = identical meaning)."""
        if not query.strip():
            return []
        scores, ids = self.index.search(embed([query]), min(k, len(self.chunks)))
        return [{**self.chunks[i], "score": float(s)} for s, i in zip(scores[0], ids[0])]