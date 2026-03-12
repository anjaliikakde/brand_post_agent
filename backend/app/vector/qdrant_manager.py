"""
Qdrant Hybrid Collection Manager.

Responsible for:
- connecting to Qdrant
- creating hybrid collections (dense + sparse)
"""

from qdrant_client import QdrantClient, models

from app.core.config import settings


class QdrantManager:
    """
    Manages Qdrant connection and hybrid collection setup.
    """

    def __init__(self):

        self.client = QdrantClient(url=settings.QDRANT_URL)

        self.collection_name = settings.QDRANT_COLLECTION

    def recreate_collection(self):
        """
        Recreate hybrid collection (dense + sparse).
        """

        if self.client.collection_exists(self.collection_name):
            self.client.delete_collection(self.collection_name)

        dense_size = self.client.get_embedding_size(
            settings.EMBEDDING_MODEL
        )

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config={
                "dense": models.VectorParams(
                    size=dense_size,
                    distance=models.Distance.COSINE
                )
            },
            sparse_vectors_config={
                "sparse": models.SparseVectorParams()
            }
        )


qdrant_manager = QdrantManager()