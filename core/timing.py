import time
from contextlib import contextmanager

@contextmanager
def timed(label):
    start = time.perf_counter()
    yield
    print(f"[TIME] {label}: {time.perf_counter() - start:.1f}s")