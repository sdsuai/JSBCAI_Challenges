"""Minimal RAG retrieval starter — the mechanics the 25-point RAG section
asks for, with no framework. Chunk -> embed -> cosine rank -> cite.

This is deliberately tiny: a few dozen lines doing what a vector DB does,
so you can SEE the math. For a real submission swap the in-memory store
for FAISS (or keep numpy — it's fine for a few thousand chunks) and the
print() loop for your backend's /rag endpoint.

Run (CPU-only, needs ~90 MB for the embedding model on first run):
    python rag_minimal.py            # embeds three toy docs, asks one query
    python rag_minimal.py --query "where is the battery?" --k 2

Pipeline steps (each maps to a README requirement):
  ingest   - split text into ~500-char chunks with the doc name + index
  embed    - all-MiniLM-L6-v2 (Sentence Transformers). Runs on CPU.
  store    - just a numpy matrix; cosine similarity = normalize + dot
  retrieve - top-k by cosine, return the chunk text + its source metadata
  cite     - print the snippets and their doc name / chunk index

Needs: pip install sentence-transformers numpy
"""

import argparse
import numpy as np

from sentence_transformers import SentenceTransformer

# Toy corpus — replace with your own blogs/PDFs (README: document ingestion).
DOCS = {
    "robot_manual.txt": (
        "The robot drives on two wheels powered by a 12V battery pack. "
        "Battery telemetry is reported at 10 Hz over UDP. Commands are "
        "sent over a reliable TCP channel and must be acknowledged."
    ),
    "networking_notes.txt": (
        "TCP guarantees in-order, reliable delivery via sequence numbers "
        "and retransmission. UDP is fire-and-forget: lower latency, but "
        "packets may be dropped or arrive out of order. Choose by whether "
        "the newest value matters more than every value."
    ),
    "memory_primer.txt": (
        "CPU RAM is virtual: the OS pages it to disk under pressure. GPU "
        "VRAM is pinned physical memory with no paging; exceed it and you "
        "get a hard OutOfMemoryError. PyTorch keeps freed VRAM in a cache "
        "until you call torch.cuda.empty_cache()."
    ),
}

CHUNK_CHARS = 500          # README: ~256-512 tokens / ~500 chars
MODEL_NAME = "all-MiniLM-L6-v2"


def chunk_text(text, doc_name, size=CHUNK_CHARS):
    """Yield (text, {doc, page}) for each fixed-size chunk of `text`."""
    for i in range(0, len(text), size):
        yield text[i:i + size], {"doc": doc_name, "page": i // size}


def build():
    """Embed every chunk of every doc. Returns (chunks, metadata, matrix)."""
    model = SentenceTransformer(MODEL_NAME)
    chunks, meta = [], []
    for name, text in DOCS.items():
        for body, md in chunk_text(text, name):
            chunks.append(body)
            meta.append(md)
    vecs = model.encode(chunks, normalize_embeddings=True)  # unit vectors
    return chunks, meta, np.asarray(vecs), model


def retrieve(query, model, matrix, chunks, meta, k=3):
    """Top-k chunks by cosine similarity (vectors are already normalized)."""
    q = model.encode([query], normalize_embeddings=True)[0]
    scores = matrix @ q                 # dot of unit vectors == cosine
    order = np.argsort(-scores)[:k]
    return [(chunks[i], meta[i], float(scores[i])) for i in order]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--query", default="how is the robot powered and how "
                                      "do its commands get delivered?")
    p.add_argument("--k", type=int, default=2)
    args = p.parse_args()

    chunks, meta, matrix, model = build()
    hits = retrieve(args.query, model, matrix, chunks, meta, k=args.k)

    print(f"[rag] query: {args.query}\n")
    for body, md, score in hits:
        print(f"--- {md['doc']} (chunk {md['page']})  score={score:.3f} ---")
        print(body.strip(), "\n")


if __name__ == "__main__":
    main()
