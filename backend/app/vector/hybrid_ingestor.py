"""
Hybrid Document Ingestor.

Converts document chunks into dense + sparse vectors
and inserts them into Qdrant.
Dense vectors: SentenceTransformer (manual)
Sparse vectors: Qdrant BM25 (fastembed)
"""

import uuid
from typing import List, Dict

from sentence_transformers import SentenceTransformer
from fastembed import SparseTextEmbedding                    # CHANGED: added import
from qdrant_client import models
from qdrant_client.models import PointStruct, SparseVector

from app.core.config import settings
from app.vector.qdrant_manager import qdrant_manager


class HybridIngestor:

    def __init__(self):
        self.client = qdrant_manager.client
        self.collection = qdrant_manager.collection_name
        self.dense_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.sparse_model = SparseTextEmbedding(model_name=settings.SPARSE_MODEL)  # CHANGED: added sparse model

    def ingest(self, chunks: List[Dict]):

        texts = [chunk["text"] for chunk in chunks]
        payloads = [{"text": chunk["text"], **chunk["metadata"]} for chunk in chunks]

        # Dense vectors — manual via SentenceTransformer
        dense_vectors = self.dense_model.encode(texts, show_progress_bar=False).tolist()

        # Sparse vectors — fastembed directly         # CHANGED: replaced _embed_sparse
        sparse_embeddings = list(self.sparse_model.embed(texts))

        points = []
        for i, (dense, sparse, payload) in enumerate(zip(dense_vectors, sparse_embeddings, payloads)):
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector={
                        "dense": dense,
                        "sparse": SparseVector(
                            indices=sparse.indices.tolist(),
                            values=sparse.values.tolist()
                        )
                    },
                    payload=payload
                )
            )

        self.client.upsert(
            collection_name=self.collection,
            points=points
        )


hybrid_ingestor = HybridIngestor()