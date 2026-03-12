from fastapi import APIRouter
from pydantic import BaseModel
import uuid
from typing import List

from app.services.generation_service import generation_service
from app.services.image_service import image_service
from app.services.render_service import render_service
from app.services.evaluation_service import evaluation_service
from app.services.rag_service import rag_service


router = APIRouter()


class PostRequest(BaseModel):
    brand_id: str            # SESSION_BRAND_ID from frontend — Qdrant namespace for RAG
    brand_context: str       # typed brand voice — fallback if RAG returns nothing
    topic: str
    document_ids: List[str] = []


@router.post("/generate")
def generate_post(request: PostRequest):

    # Step 1 — Generate text
    # RAG pulls from Qdrant using brand_id; falls back to brand_context if empty
    generation = generation_service.generate_post(
        topic=request.topic,
        brand_id=request.brand_id,
        brand_context=request.brand_context
    )

    text_output = generation["text_output"]

    # Step 2 — Parse headline + caption from generated text
    lines = text_output.strip().splitlines()
    headline = lines[0].strip() if lines else "Generated Post"
    caption = "\n".join(lines[1:]).strip() if len(lines) > 1 else text_output

    # Step 3 — Generate image
    post_id = str(uuid.uuid4())

    image = image_service.generate_image(
        prompt=f"{headline}. {caption[:200]}",
        image_name=f"{post_id}.png"
    )

    # Step 4 — Render final post as PNG via Playwright
    rendered = render_service.render_post(
        post_id=post_id,
        headline=headline,
        caption=caption,
        image_path=image["image_path"]
    )

    # Step 5 — Evaluate with LLM-as-judge
    context = rag_service.build_context_block(
        query=request.topic,
        brand_id=request.brand_id
    ) or request.brand_context

    evaluation = evaluation_service.evaluate_post(
        brand_context=context,
        caption=caption
    )

    # Flat response — all fields at top level so frontend can read directly
    return {
        "post_id": post_id,
        "headline": headline,
        "caption": caption,
        "image_path": image["image_path"],       # frontend reads result.image_path
        "image_url": image["image_url"],
        "evaluation": evaluation["evaluation"],  # unwrapped string — frontend JSON.parses it
    }