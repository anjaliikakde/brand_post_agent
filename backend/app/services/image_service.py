"""
Image Generation Service

Uses Replicate API to generate images from prompts.
Images are saved locally using storage_service.
"""

import requests
from typing import Dict
import replicate

from app.core.config import settings
from app.services.storage_service import storage_service


class ImageService:
    """
    Handles image generation through Replicate.
    """

    def __init__(self):
        # Replicate uses environment variable authentication
        self.client = replicate.Client(api_token=settings.REPLICATE_API_TOKEN)

        # flux-schnell works without a version hash; fast and high quality
        self.model = "black-forest-labs/flux-schnell"

    # -----------------------------------------
    # IMAGE GENERATION
    # -----------------------------------------

    def generate_image(self, prompt: str, image_name: str) -> Dict:
        """
        Generate image using Replicate and save locally.
        """

        try:
            output = self.client.run(
                self.model,
                input={
                    "prompt": prompt,
                    "num_outputs": 1,
                    "width": 1024,
                    "height": 1024,
                },
            )
        except Exception as e:
            raise RuntimeError(f"Replicate generation failed: {e}")

        # Output can be a generator or list — consume it safely
        output_list = list(output) if output else []

        if not output_list:
            raise RuntimeError("Replicate returned no image")

        image_url = str(output_list[0])  # coerce FileOutput/URL object to string

        # Download image with timeout to prevent hanging
        response = requests.get(image_url, timeout=30)

        if response.status_code != 200:
            raise RuntimeError(f"Failed to download generated image: HTTP {response.status_code}")

        image_path = storage_service.save_generated_image(
            image_name=image_name,
            image_bytes=response.content,
        )

        return {
            "image_path": str(image_path),
            "image_url": image_url,
        }


image_service = ImageService()