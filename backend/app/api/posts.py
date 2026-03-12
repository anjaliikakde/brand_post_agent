from fastapi import APIRouter
from pydantic import BaseModel
import uuid

from app.services.generation_service import generation_service
from app.services.image_service import image_service
from app.services.render_service import render_service
from app.services.evaluation_service import evaluation_service
from app.services.rag_service import rag_service


router = APIRouter()


class PostRequest(BaseModel):
    brand_id: str
    topic: str


@router.post("/generate")
def generate_post(request: PostRequest):

    # Step 1 — Generate text
    generation = generation_service.generate_post(
        topic=request.topic,
        brand_id=request.brand_id
    )

    text_output = generation["text_output"]

    # Step 2 — naive parsing
    headline = "Generated Headline"
    caption = text_output
    image_prompt = text_output

    # Step 3 — image generation
    post_id = str(uuid.uuid4())

    image = image_service.generate_image(
        prompt=image_prompt,
        image_name=f"{post_id}.png"
    )

    # Step 4 — render final post
    rendered = render_service.render_post(
        post_id=post_id,
        headline=headline,
        caption=caption,
        image_path=image["image_path"]
    )

    # Step 5 — evaluation
    context = rag_service.build_context_block(
        query=request.topic,
        brand_id=request.brand_id
    )

    evaluation = evaluation_service.evaluate_post(
        brand_context=context,
        caption=caption
    )

    return {
        "post_id": post_id,
        "headline": headline,
        "caption": caption,
        "image": image,
        "rendered": rendered,
        "evaluation": evaluation
    }