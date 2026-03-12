from fastapi import APIRouter, UploadFile, File

from app.services.document_service import document_service


router = APIRouter()


@router.post("/brands/{brand_id}/documents")
async def upload_document(
    brand_id: str,
    file: UploadFile = File(...)
):

    content = await file.read()

    result = document_service.upload_document(
        brand_id=brand_id,
        file_name=file.filename,
        file_bytes=content
    )

    return result