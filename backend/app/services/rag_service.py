"""
RAG Service

Responsible for retrieving brand-specific context
from Qdrant using hybrid search.

Hybrid search combines:
- dense vector embeddings
- BM25 sparse keyword search
- RRF fusion ranking
"""

from typing import List

from app.vector.hybrid_searcher import hybrid_searcher
from app.core.config import settings


class RAGService:
    """
    Handles retrieval of relevant brand context.
    """

    def __init__(self):

        self.top_k = settings.TOP_K_RESULTS

    # -----------------------------------------
    # CONTEXT RETRIEVAL
    # -----------------------------------------

    def retrieve_context(self, query: str, brand_id: str) -> List[str]:
        """
        Retrieve relevant chunks for a query.
        """

        results = hybrid_searcher.search(
            query=query,
            brand_id=brand_id,
            top_k=self.top_k,
        )

        context_chunks = []

        for r in results:

            text = r.get("text")

            if text:
                context_chunks.append(text)

        return context_chunks

    # -----------------------------------------
    # FORMAT CONTEXT FOR PROMPT
    # -----------------------------------------

    def build_context_block(self, query: str, brand_id: str) -> str:
        """
        Format retrieved chunks into a prompt context block.
        """

        chunks = self.retrieve_context(query, brand_id)

        if not chunks:
            return ""

        context_block = "\n\n".join(chunks)

        return context_block


rag_service = RAGService()