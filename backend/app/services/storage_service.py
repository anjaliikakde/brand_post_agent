"""
Storage Service

Handles all filesystem operations for the application.

Nothing else in the system should write directly to disk.
All file operations must go through this service.
"""

from pathlib import Path
import json
from typing import Dict, Any

from app.core.config import settings


class StorageService:
    """
    Centralized filesystem storage manager.
    """

    def __init__(self):

        self.base_path = Path(settings.STORAGE_PATH)

        self.brands_path = self.base_path / "brands"
        self.posts_path = self.base_path / "posts"
        self.images_path = self.base_path / "images"
        self.jobs_path = self.base_path / "jobs"

        self._create_directories()

    def _create_directories(self):
        """
        Ensure storage directories exist.
        """

        for path in [
            self.brands_path,
            self.posts_path,
            self.images_path,
            self.jobs_path,
        ]:
            path.mkdir(parents=True, exist_ok=True)

    # ----------------------------------------
    # Brand Storage
    # ----------------------------------------

    def get_brand_path(self, brand_id: str) -> Path:

        brand_path = self.brands_path / brand_id
        brand_path.mkdir(parents=True, exist_ok=True)

        return brand_path

    def save_brand_document(self, brand_id: str, file_name: str, file_bytes: bytes) -> Path:
        """
        Save uploaded brand document.
        """

        brand_path = self.get_brand_path(brand_id)

        docs_path = brand_path / "documents"
        docs_path.mkdir(exist_ok=True)

        file_path = docs_path / file_name

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        return file_path

    # ----------------------------------------
    # Post Storage
    # ----------------------------------------

    def create_post_folder(self, post_id: str) -> Path:

        post_path = self.posts_path / post_id
        post_path.mkdir(parents=True, exist_ok=True)

        return post_path

    def save_post_metadata(self, post_id: str, metadata: Dict[str, Any]) -> Path:

        post_path = self.create_post_folder(post_id)

        metadata_file = post_path / "post.json"

        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        return metadata_file

    # ----------------------------------------
    # Image Storage
    # ----------------------------------------

    def save_generated_image(self, image_name: str, image_bytes: bytes) -> Path:

        image_path = self.images_path / image_name

        with open(image_path, "wb") as f:
            f.write(image_bytes)

        return image_path

    # ----------------------------------------
    # Job Storage
    # ----------------------------------------

    def save_job(self, job_id: str, data: Dict[str, Any]):

        job_file = self.jobs_path / f"{job_id}.json"

        with open(job_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_job(self, job_id: str) -> Dict[str, Any]:

        job_file = self.jobs_path / f"{job_id}.json"

        if not job_file.exists():
            return {}

        with open(job_file) as f:
            return json.load(f)


storage_service = StorageService()