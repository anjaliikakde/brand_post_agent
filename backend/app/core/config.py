"""
Global application configuration.

Loads environment variables and exposes them through
a single settings object used across the backend.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """

    # ---------- API Keys ----------
    OPENAI_API_KEY: str
    REPLICATE_API_TOKEN: str

    # ---------- Qdrant ----------
    # QDRANT_URL: str = "http://localhost:6333"
    # QDRANT_COLLECTION: str = "brand_knowledge"
    # ---------- Qdrant ----------
    QDRANT_URL: str = "http://localhost:6333"
    
    QDRANT_COLLECTION: str = "brand_knowledge"
    QDRANT_HOST: str = "localhost"      # add this
    QDRANT_PORT: int = 6333             # add this
        

    # ---------- Embeddings ----------
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    SPARSE_MODEL: str = "Qdrant/bm25"

    # ---------- Redis ----------
    REDIS_URL: str = "redis://localhost:6379"

    # ---------- RAG ----------
    CHUNK_SIZE: int = 300
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 5

    # ---------- Storage ----------
    STORAGE_PATH: str = "storage"

    class Config:
        env_file = ".env"


settings = Settings()