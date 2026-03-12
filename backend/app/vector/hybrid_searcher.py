"""
Hybrid Searcher.

Performs hybrid retrieval using:
dense vectors + BM25 sparse vectors + RRF fusion.
"""

from typing import List, Dict

from qdrant_client import models

from app.core.config import settings
from app.vector.qdrant_manager import qdrant_manager


class HybridSearcher:

    def __init__(self):

        self.client = qdrant_manager.client
        self.collection = qdrant_manager.collection_name

    def search(
        self,
        query: str,
        brand_id: str,
        top_k: int = 5,
        prefetch_k: int = 20
    ) -> List[Dict]:

        prefetch = [

            models.Prefetch(
                query=models.Document(
                    text=query,
                    model=settings.EMBEDDING_MODEL
                ),
                using="dense",
                limit=prefetch_k
            ),

            models.Prefetch(
                query=models.Document(
                    text=query,
                    model=settings.SPARSE_MODEL
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