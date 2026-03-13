"""
Hybrid Searcher.

Performs hybrid retrieval using:
dense vectors (manual SentenceTransformer) + BM25 sparse vectors + RRF fusion.
"""

from typing import List, Dict

from qdrant_client import models
from sentence_transformers import SentenceTransformer
from fastembed import SparseTextEmbedding

from app.core.config import settings
from app.vector.qdrant_manager import qdrant_manager


class HybridSearcher:

    def __init__(self):
        self.client = qdrant_manager.client
        self.collection = qdrant_manager.collection_name
        # Same models used in hybrid_ingestor — must match exactly
        self.dense_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.sparse_model = SparseTextEmbedding(model_name=settings.SPARSE_MODEL)

    def search(
        self,
        query: str,
        brand_id: str,
        top_k: int = 5,
        prefetch_k: int = 20
    ) -> List[Dict]:

        # Embed query manually — same approach as ingestor
        # models.Document only supports fastembed registry, not HuggingFace models
        dense_vector = self.dense_model.encode(query).tolist()
        sparse_result = list(self.sparse_model.embed([query]))[0]

        prefetch = [
            models.Prefetch(
                query=dense_vector,
                using="dense",
                limit=prefetch_k
            ),
            models.Prefetch(
                query=models.SparseVector(
                    indices=sparse_result.indices.tolist(),
                    values=sparse_result.values.tolist()
                ),
                using="sparse",
                limit=prefetch_k
            )
        ]

        result = self.client.query_points(
            collection_name=self.collection,
            query=models.FusionQuery(
                fusion=models.Fusion.RRF
            ),
            prefetch=prefetch,
            limit=top_k,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="brand_id",
                        match=models.MatchValue(value=brand_id)
                    )
                ]
            ),
            with_payload=True
        )

        return [point.payload for point in result.points]


hybrid_searcher = HybridSearcher()