"""
Document Service

Handles brand document uploads and triggers
the ingestion pipeline.
"""

from pathlib import Path
from typing import Dict

from app.services.storage_service import storage_service
from app.services.ingestion_service import ingestion_service


class DocumentService:
    """
    Manages brand document uploads.
    """

    # -----------------------------------------
    # UPLOAD DOCUMENT
    # -----------------------------------------

    def upload_document(
        self,
        brand_id: str,
        file_name: str,
        file_bytes: bytes
    ) -> Dict:

        # Save file using storage service
        file_path = storage_service.save_brand_document(
            brand_id=brand_id,
            file_name=file_name,
            file_bytes=file_bytes
        )

        # Trigger ingestion pipeline
        ingestion_result = ingestion_service.ingest_pdf(
            pdf_path=str(file_path),
            brand_id=brand_id
        )

        return {
            "brand_id": brand_id,
            "file_name": file_name,
            "file_path": str(file_path),
            "ingestion_result": ingestion_result
        }


document_service = DocumentService()