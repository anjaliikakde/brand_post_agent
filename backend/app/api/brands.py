from fastapi import APIRouter
from pydantic import BaseModel

from app.services.brand_service import brand_service
 

router = APIRouter()


class BrandCreateRequest(BaseModel):
    name: str
    description: str
    tone: str


@router.post("/brands")
def create_brand(request: BrandCreateRequest):

    brand = brand_service.create_brand(
        name=request.name,
        description=request.description,
        tone=request.tone
    )

    return brand


@router.get("/brands")
def list_brands():

    return brand_service.list_brands()


@router.get("/brands/{brand_id}")
def get_brand(brand_id: str):

    return brand_service.get_brand(brand_id)