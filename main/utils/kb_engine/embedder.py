"""FastEmbed dense vector embedding provider for hybrid retrieval."""

from __future__ import annotations

import struct
from collections.abc import Sequence

from fastembed import TextEmbedding

_MODEL_NAME = "BAAI/bge-small-en-v1.5"
_EMBEDDING_DIM = 384


class PassageEmbedder:
    """Singleton FastEmbed wrapper providing ONNX-accelerated dense embeddings."""

    _model: TextEmbedding | None = None

    @classmethod
    def get_model(cls) -> TextEmbedding:
        if cls._model is None:
            cls._model = TextEmbedding(model_name=_MODEL_NAME)
        return cls._model

    @classmethod
    def embed_texts_to_bytes(
        cls,
        texts: Sequence[str],
        batch_size: int = 128,
    ) -> list[bytes]:
        """Embed a sequence of texts and return raw float384 bytes for SQLite."""
        if not texts:
            return []
        model = cls.get_model()
        results: list[bytes] = []
        for vec in model.embed(texts, batch_size=batch_size):
            results.append(struct.pack(f"{_EMBEDDING_DIM}f", *vec))
        return results

    @classmethod
    def embed_query_to_bytes(cls, query: str) -> bytes:
        """Embed a single query string and return raw float384 bytes."""
        model = cls.get_model()
        vec = next(model.embed([query]))
        return struct.pack(f"{_EMBEDDING_DIM}f", *vec)

    @classmethod
    def embedding_dim(cls) -> int:
        return _EMBEDDING_DIM
