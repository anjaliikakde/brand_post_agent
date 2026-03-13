"""
Document Ingestion Service

Pipeline:

File → Extract text (by type) → Normalize → Filter → Chunk → Hybrid Vector Ingestion

Supported formats:
- PDF  → PyMuPDF
- TXT / MD → plain text read
- DOCX → python-docx
"""

import re
from pathlib import Path
from typing import List, Dict

import fitz  # PyMuPDF

from langchain_text_splitters import RecursiveCharacterTextSplitter  # CHANGED

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
    # EXTRACTION — route by file type
    # -----------------------------------------

    def extract(self, file_path: Path) -> List[Dict]:
        """
        Route to the correct extractor based on file extension.
        """
        ext = file_path.suffix.lower()

        if ext == ".pdf":
            return self.extract_pdf(file_path)
        elif ext in (".txt", ".md"):
            return self.extract_text(file_path)
        elif ext in (".doc", ".docx"):
            return self.extract_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def extract_pdf(self, pdf_path: Path) -> List[Dict]:
        """
        Extract page-level text from PDF using PyMuPDF.
        """
        documents = []

        with fitz.open(str(pdf_path)) as pdf:
            for page_index in range(pdf.page_count):
                page = pdf.load_page(page_index)
                text = page.get_text("text")

                if not text or not text.strip():
                    continue

                documents.append({
                    "text": text.strip(),
                    "metadata": {
                        "page": page_index + 1,
                        "source": pdf_path.name,
                        "char_count": len(text),
                    },
                })

        return documents

    def extract_text(self, file_path: Path) -> List[Dict]:
        """
        Extract text from plain .txt or .md files.
        Treats the whole file as one document.
        """
        text = file_path.read_text(encoding="utf-8", errors="ignore").strip()

        if not text:
            return []

        return [{
            "text": text,
            "metadata": {
                "page": 1,
                "source": file_path.name,
                "char_count": len(text),
            },
        }]

    def extract_docx(self, file_path: Path) -> List[Dict]:
        """
        Extract text from .docx files using python-docx.
        Each paragraph becomes its own document entry.
        """
        try:
            import docx
        except ImportError:
            raise ImportError(
                "python-docx is required for .docx files. "
                "Run: pip install python-docx"
            )

        doc = docx.Document(str(file_path))
        documents = []

        for i, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if not text:
                continue
            documents.append({
                "text": text,
                "metadata": {
                    "page": i + 1,
                    "source": file_path.name,
                    "char_count": len(text),
                },
            })

        return documents

    # -----------------------------------------
    # TEXT NORMALIZATION
    # -----------------------------------------

    def normalize_text(self, text: str) -> str:
        """
        Clean extraction artifacts.
        """
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
        return text.strip()

    def normalize_documents(self, docs: List[Dict]) -> List[Dict]:
        return [
            {"text": self.normalize_text(doc["text"]), "metadata": doc["metadata"]}
            for doc in docs
        ]

    # -----------------------------------------
    # DOCUMENT FILTERING
    # -----------------------------------------

    def filter_documents(self, docs: List[Dict]) -> List[Dict]:
        """
        Remove noisy or low-value pages.
        For non-PDF files skip the char_count filter since
        plain text brand docs can be short.
        """
        filtered = []

        noise_markers = [
            "isbn", "copyright", "table of contents",
            "publisher", "all rights reserved",
        ]

        for doc in docs:
            text = doc["text"].lower()
            source = doc["metadata"].get("source", "")
            ext = Path(source).suffix.lower()

            # Only apply length filter to PDFs
            if ext == ".pdf" and doc["metadata"]["char_count"] < 200:
                continue

            if any(marker in text for marker in noise_markers):
                continue

            filtered.append(doc)

        return filtered

    # -----------------------------------------
    # TEXT CHUNKING — LangChain RecursiveCharacterTextSplitter
    # -----------------------------------------

    def chunk_documents(self, docs: List[Dict]) -> List[Dict]:
        """
        Split documents into overlapping chunks using LangChain
        RecursiveCharacterTextSplitter.
        chunk_size is in characters (set CHUNK_SIZE=1500 in config).
        brand_id is attached separately after chunking.
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        chunks = []

        for doc in docs:
            splits = splitter.split_text(doc["text"])
            for split in splits:
                if not split.strip():
                    continue
                chunks.append({
                    "text": split.strip(),
                    "metadata": {**doc["metadata"]},
                })

        return chunks

    # -----------------------------------------
    # FULL INGESTION PIPELINE
    # -----------------------------------------

    def ingest_document(self, file_path: str, brand_id: str) -> Dict:
        """
        Full ingestion pipeline — works for PDF, TXT, MD, DOCX.
        Single entry point. Routes by file extension internally.
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.stat().st_size == 0:
            raise ValueError(f"File is empty: {file_path.name}")

        # 1 Extract text — routed by file type via self.extract()
        documents = self.extract(file_path)

        if not documents:
            raise ValueError(f"No text could be extracted from: {file_path.name}")

        # 2 Normalize
        normalized = self.normalize_documents(documents)

        # 3 Filter noise
        filtered = self.filter_documents(normalized)

        # Fall back to normalized if filter removes everything
        if not filtered:
            filtered = normalized

        # 4 Chunk
        chunks = self.chunk_documents(filtered)

        # 5 Attach brand_id to every chunk payload
        for chunk in chunks:
            chunk["metadata"]["brand_id"] = brand_id

        # 6 Ingest into Qdrant
        hybrid_ingestor.ingest(chunks)

        return {
            "pages_extracted": len(documents),
            "chunks_created": len(chunks),
            "brand_id": brand_id,
            "file_name": file_path.name,
        }

    def ingest_pdf(self, pdf_path: str, brand_id: str) -> Dict:
        """
        Alias kept so nothing else breaks if called directly.
        """
        return self.ingest_document(pdf_path, brand_id)


ingestion_service = IngestionService()