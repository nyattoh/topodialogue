import hashlib
import numpy as np
from typing import Protocol

class Embedder(Protocol):
    def embed(self, texts: list[str]) -> np.ndarray: ...

class FakeEmbedder:
    """Stable hashed bag-of-character-ngram vectors; no network/model download."""
    def __init__(self, dimensions: int = 64): self.dimensions = dimensions
    def embed(self, texts: list[str]) -> np.ndarray:
        rows = []
        for text in texts:
            v = np.zeros(self.dimensions, dtype=float)
            normalized = text.casefold()
            grams = [normalized[i:i+3] for i in range(max(1, len(normalized)-2))]
            for gram in grams:
                digest = hashlib.blake2b(gram.encode(), digest_size=8).digest()
                idx = int.from_bytes(digest, "big") % self.dimensions
                v[idx] += 1
            norm = np.linalg.norm(v)
            rows.append(v / norm if norm else v)
        return np.asarray(rows)

class SentenceTransformerEmbedder:
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
    def embed(self, texts: list[str]) -> np.ndarray:
        return np.asarray(self.model.encode(texts, normalize_embeddings=True))

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denom) if denom else 0.0
