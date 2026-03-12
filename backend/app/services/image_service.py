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
        self.client = replicate.Client(api_token=settings.REPLICATE_API_TOKEN)

        # flux-dev: significantly better quality than flux-schnell
        # flux-1.1-pro is the best but costs more — swap if budget allows
        self.model = "black-forest-labs/flux-dev"

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
                    "num_inference_steps": 28,   # flux-dev sweet spot (schnell uses 4)
                    "guidance": 3.5,              # prompt adherence — 3-4 is ideal for flux-dev
                    "output_format": "png",
                    "output_quality": 100,
                },
            )
        except Exception as e:
            raise RuntimeError(f"Replicate generation failed: {e}")

        output_list = list(output) if output else []

        if not output_list:
            raise RuntimeError("Replicate returned no image")

        image_url = str(output_list[0])

        response = requests.get(image_url, timeout=60)  # flux-dev is slower, increase timeout

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