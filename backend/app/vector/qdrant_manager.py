"""
Qdrant Hybrid Collection Manager.
"""

from qdrant_client import QdrantClient, models
from app.core.config import settings


class QdrantManager:

    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection_name = settings.QDRANT_COLLECTION

    def recreate_collection(self):

        if self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config={
                "dense": models.VectorParams(
                    size=384,  # MiniLM-L6-v2 fixed output dim
                    distance=models.Distance.COSINE
                )
            },
            sparse_vectors_config={
                "sparse": models.SparseVectorParams()
            }
        )


qdrant_manager = QdrantManager()