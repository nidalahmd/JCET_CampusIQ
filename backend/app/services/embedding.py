import hashlib
import math
import re
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.core.config import get_settings

VECTOR_DIMENSION = 1536


class BaseEmbeddingService(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> list[float]:
        """Generate embedding vector for single text."""
        pass

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embedding vectors for a list of texts."""
        pass


class LocalFallbackEmbeddingService(BaseEmbeddingService):
    """Deterministic, normalized 1536-dimensional embedding generator.

    Provides stable semantic-hash vector representations for local development,
    offline runs, and automated unit testing without external API dependencies.
    """

    def _generate_vector(self, text: str) -> list[float]:
        vec = [0.0] * VECTOR_DIMENSION
        if not text or not text.strip():
            vec[0] = 1.0
            return vec

        # Tokenize words and character n-grams
        tokens = re.findall(r"\w+", text.lower())
        if not tokens:
            tokens = [text.strip()]

        for i, token in enumerate(tokens):
            # Positional token hashing
            token_hash = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
            idx1 = token_hash % VECTOR_DIMENSION
            idx2 = (token_hash >> 16) % VECTOR_DIMENSION
            weight = 1.0 / math.sqrt(i + 1)
            vec[idx1] += weight
            vec[idx2] += weight * 0.5

            # 3-gram sub-tokens for subword matching
            for j in range(max(0, len(token) - 2)):
                ngram = token[j : j + 3]
                ng_hash = int(hashlib.md5(ngram.encode("utf-8")).hexdigest(), 16)
                idx_ng = ng_hash % VECTOR_DIMENSION
                vec[idx_ng] += 0.25

        # L2-normalize vector
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        else:
            vec[0] = 1.0

        return vec

    def embed_text(self, text: str) -> list[float]:
        return self._generate_vector(text)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self._generate_vector(t) for t in texts]


class GeminiEmbeddingService(BaseEmbeddingService):
    """Google Gemini Embedding API integration with fallback support."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.fallback = LocalFallbackEmbeddingService()
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent"
        self.batch_endpoint = "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:batchEmbedContents"

    def embed_text(self, text: str) -> list[float]:
        if not self.api_key or not text.strip():
            return self.fallback.embed_text(text)

        try:
            url = f"{self.endpoint}?key={self.api_key}"
            payload = {
                "model": "models/text-embedding-004",
                "content": {"parts": [{"text": text[:2048]}]},
                "outputDimensionality": VECTOR_DIMENSION,
            }
            with httpx.Client(timeout=10.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    values: list[float] = data.get("embedding", {}).get("values", [])
                    if values:
                        return self._pad_or_truncate(values)
        except Exception:
            pass

        return self.fallback.embed_text(text)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key or not texts:
            return self.fallback.embed_batch(texts)

        results: list[list[float]] = []
        for text in texts:
            results.append(self.embed_text(text))
        return results

    def _pad_or_truncate(self, values: list[float]) -> list[float]:
        if len(values) == VECTOR_DIMENSION:
            return values
        if len(values) > VECTOR_DIMENSION:
            return values[:VECTOR_DIMENSION]
        # Pad with zeros and re-normalize
        padded = values + [0.0] * (VECTOR_DIMENSION - len(values))
        norm = math.sqrt(sum(x * x for x in padded))
        return [x / norm for x in padded] if norm > 0 else padded


def get_embedding_service() -> BaseEmbeddingService:
    settings = get_settings()
    api_key = settings.gemini_api_key or settings.embedding_api_key
    if api_key and api_key.strip():
        return GeminiEmbeddingService(api_key=api_key.strip())
    return LocalFallbackEmbeddingService()
