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

        # Stable and widely used diffusion model on Replicate
        self.model = "stability-ai/sdxl"

    # -----------------------------------------
    # IMAGE GENERATION
    # -----------------------------------------

    def generate_image(self, prompt: str, image_name: str) -> Dict:
        """
        Generate image using Replicate and save locally.
        """

        output = self.client.run(
            self.model,
            input={
                "prompt": prompt,
                "num_outputs": 1,
                "width": 1024,
                "height": 1024,
            },
        )

        if not output:
            raise RuntimeError("Replicate returned no image")

        image_url = output[0]

        # Download image
        response = requests.get(image_url)

        if response.status_code != 200:
            raise RuntimeError("Failed to download generated image")

        image_path = storage_service.save_generated_image(
            image_name=image_name,
            image_bytes=response.content,
        )

        return {
            "image_path": str(image_path),
            "image_url": image_url,
        }


image_service = ImageService()