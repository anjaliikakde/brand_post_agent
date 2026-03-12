"""
Document Ingestion Service

Pipeline:

PDF → Extract text → Normalize → Filter → Chunk → Hybrid Vector Ingestion

Uses:
- PyMuPDF for PDF parsing
- Qdrant hybrid ingestion (dense + sparse)
"""

import re
from pathlib import Path
from typing import List, Dict

import fitz  # PyMuPDF

from app.vector.hybrid_ingestor import hybrid_ingestor
from app.core.config import settings


class IngestionService:
    """
    Handles ingestion of brand documents into the vector database.
    """

    def __init__(self):

        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP

    # -----------------------------------------
    # PDF TEXT EXTRACTION
    # -----------------------------------------

    def extract_pdf(self, pdf_path: Path) -> List[Dict]:
        """
        Extract page-level text from PDF.
        """

        documents = []

        with fitz.open(pdf_path) as pdf:

            for page_index in range(pdf.page_count):

                page = pdf.load_page(page_index)

                text = page.get_text("text")

                if not text or not text.strip():
                    continue

                documents.append(
                    {
                        "text": text.strip(),
                        "metadata": {
                            "page": page_index + 1,
                            "source": pdf_path.name,
                            "char_count": len(text),
                        },
                    }
                )

        return documents

    # -----------------------------------------
    # TEXT NORMALIZATION
    # -----------------------------------------

    def normalize_text(self, text: str) -> str:
        """
        Clean PDF artifacts.
        """

        text = text.replace("\r\n", "\n").replace("\r", "\n")

        text = re.sub(r"\n{3,}", "\n\n", text)

        text = re.sub(r"[ \t]{2,}", " ", text)

        text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

        return text.strip()

    def normalize_documents(self, docs: List[Dict]) -> List[Dict]:

        normalized = []

        for doc in docs:

            normalized.append(
                {
                    "text": self.normalize_text(doc["text"]),
                    "metadata": doc["metadata"],
                }
            )

        return normalized

    # -----------------------------------------
    # DOCUMENT FILTERING
    # -----------------------------------------

    def filter_documents(self, docs: List[Dict]) -> List[Dict]:
        """
        Remove noisy or low-value pages.
        """

        filtered = []

        noise_markers = [
            "isbn",
            "copyright",
            "table of contents",
            "publisher",
            "all rights reserved",
        ]

        for doc in docs:

            text = doc["text"].lower()

            if doc["metadata"]["char_count"] < 200:
                continue

            if any(marker in text for marker in noise_markers):
                continue

            filtered.append(doc)

        return filtered

    # -----------------------------------------
    # TEXT CHUNKING
    # -----------------------------------------

    def chunk_documents(self, docs: List[Dict]) -> List[Dict]:
        """
        Split documents into overlapping chunks.
        """

        chunks = []

        for doc in docs:

            words = doc["text"].split()

            start = 0

            while start < len(words):

                end = start + self.chunk_size

                chunk_words = words[start:end]

                chunk_text = " ".join(chunk_words)

                chunks.append(
                    {
                        "text": chunk_text,
                        "metadata": {
                            **doc["metadata"],
                        },
                    }
                )

                start = end - self.chunk_overlap

        return chunks

    # -----------------------------------------
    # FULL INGESTION PIPELINE
    # -----------------------------------------

    def ingest_pdf(self, pdf_path: str, brand_id: str) -> Dict:
        """
        Full ingestion pipeline.
        """

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # 1 Extract text
        documents = self.extract_pdf(pdf_path)

        # 2 Normalize
        normalized = self.normalize_documents(documents)

        # 3 Filter noise
        filtered = self.filter_documents(normalized)

        # 4 Chunk documents
        chunks = self.chunk_documents(filtered)

        # 5 Attach brand_id metadata
        for chunk in chunks:
            chunk["metadata"]["brand_id"] = brand_id

        # 6 Hybrid ingestion
        hybrid_ingestor.ingest(chunks)

        return {
            "pages_extracted": len(documents),
            "chunks_created": len(chunks),
            "brand_id": brand_id,
        }


ingestion_service = IngestionService()