import os
import json
import numpy as np

# 1. Absolute Pathing Setup (The Enterprise Fix)
current_dir = os.path.dirname(os.path.abspath(__file__))
directory = current_dir

try:
    import faiss
except ImportError:
    raise ImportError("Run: pip install faiss-cpu")
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError("Run: pip install sentence-transformers")

# Model + Index Variables
_MODEL_NAME = "all-MiniLM-L6-v2"   
_model: SentenceTransformer = None
_index: faiss.IndexFlatL2   = None
_metadata: list[dict]       = []   
_DIM = 384

def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print("[VectorStore] Loading embedding model...")
        _model = SentenceTransformer(_MODEL_NAME)
    return _model

def _get_index() -> faiss.IndexFlatL2:
    global _index
    if _index is None:
        _index = faiss.IndexFlatL2(_DIM)
    return _index

def _embed(text: str) -> np.ndarray:
    model = _get_model()
    vec = model.encode([text], convert_to_numpy=True).astype("float32")
    return vec

def add_memory(text: str, metadata: dict = None) -> int:
    from datetime import datetime

    vec = _embed(text)
    idx = _get_index()
    idx.add(vec)

    entry = {
        "text":      text,
        "metadata":  metadata or {},
        "stored_at": datetime.now().isoformat(),
        "position":  len(_metadata),
    }
    _metadata.append(entry)
    return entry["position"]

def search(query: str, k: int = 3) -> list[dict]:
    idx = _get_index()
    if idx.ntotal == 0:
        return []

    k = min(k, idx.ntotal)
    vec = _embed(query)
    distances, positions = idx.search(vec, k)

    results = []
    for dist, pos in zip(distances[0], positions[0]):
        if pos == -1:
            continue
        entry = dict(_metadata[pos])
        entry["distance"] = float(dist)
        results.append(entry)

    return results

def format_results(results: list[dict]) -> str:
    if not results:
        return "No relevant memories found."

    lines = ["--- Relevant Memory ---"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['text']}")
        if r.get("metadata"):
            lines.append(f"   (source: {r['metadata']})")
    lines.append("--- End of Memory ---")
    return "\n".join(lines)

def count() -> int:
    return _get_index().ntotal

# --- The Fixed Save & Load Functions ---

def save(target_dir: str = directory) -> None:
    os.makedirs(target_dir, exist_ok=True)
    faiss.write_index(_get_index(), os.path.join(target_dir, "faiss.index"))
    with open(os.path.join(target_dir, "metadata.json"), "w") as f:
        json.dump(_metadata, f, indent=2)
    print(f"[VectorStore] Saved {count()} memories to '{target_dir}/'")

def load(target_dir: str = directory) -> None:
    global _index, _metadata

    index_path    = os.path.join(target_dir, "faiss.index")
    metadata_path = os.path.join(target_dir, "metadata.json")

    if not os.path.exists(index_path):
        print(f"[VectorStore] No saved index found at '{target_dir}/' — starting fresh.")
        return

    _index = faiss.read_index(index_path)
    with open(metadata_path) as f:
        _metadata = json.load(f)
    print(f"[VectorStore] Loaded {count()} memories from '{target_dir}/'")