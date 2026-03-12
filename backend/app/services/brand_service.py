"""
Brand Service

Responsible for managing brands in the system.

Brand metadata is stored locally in:
storage/brands/{brand_id}/brand.json
"""

import json
from pathlib import Path
from typing import Dict, List
import uuid

from app.services.storage_service import storage_service


class BrandService:
    """
    Manages brand metadata and brand storage.
    """

    # -----------------------------------------
    # CREATE BRAND
    # -----------------------------------------

    def create_brand(self, name: str, description: str, tone: str) -> Dict:

        brand_id = str(uuid.uuid4())

        brand_folder = storage_service.get_brand_path(brand_id)

        brand_metadata = {
            "brand_id": brand_id,
            "name": name,
            "description": description,
            "tone": tone
        }

        metadata_path = brand_folder / "brand.json"

        with open(metadata_path, "w") as f:
            json.dump(brand_metadata, f, indent=2)

        return brand_metadata

    # -----------------------------------------
    # GET BRAND
    # -----------------------------------------

    def get_brand(self, brand_id: str) -> Dict:

        brand_folder = storage_service.get_brand_path(brand_id)

        metadata_path = brand_folder / "brand.json"

        if not metadata_path.exists():
            raise FileNotFoundError("Brand not found")

        with open(metadata_path) as f:
            return json.load(f)

    # -----------------------------------------
    # LIST BRANDS
    # -----------------------------------------

    def list_brands(self) -> List[Dict]:

        brands = []

        brands_root = Path("storage/brands")

        if not brands_root.exists():
            return brands

        for brand_folder in brands_root.iterdir():

            metadata_file = brand_folder / "brand.json"

            if metadata_file.exists():

                with open(metadata_file) as f:
                    brands.append(json.load(f))

        return brands


brand_service = BrandService()