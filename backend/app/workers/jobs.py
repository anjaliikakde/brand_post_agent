"""
Worker Jobs

Defines background tasks executed by RQ workers.
"""

import uuid

from app.services.ingestion_service import ingestion_service
from app.services.generation_service import generation_service
from app.services.image_service import image_service
from app.services.render_service import render_service
from app.services.evaluation_service import evaluation_service
from app.services.rag_service import rag_service
from app.services.storage_service import storage_service


# -----------------------------------------
# DOCUMENT INGESTION JOB
# -----------------------------------------

def ingest_document_job(pdf_path: str, brand_id: str):

    result = ingestion_service.ingest_pdf(
        pdf_path=pdf_path,
        brand_id=brand_id
    )

    return result


# -----------------------------------------
# POST GENERATION JOB
# -----------------------------------------

def generate_post_job(topic: str, brand_id: str):

    post_id = str(uuid.uuid4())

    generation_result = generation_service.generate_post(
        topic=topic,
        brand_id=brand_id
    )

    text_output = generation_result["text_output"]

    # For simplicity we keep full output
    post_metadata = {
        "post_id": post_id,
        "brand_id": brand_id,
        "topic": topic,
        "text_output": text_output
    }

    storage_service.save_post_metadata(post_id, post_metadata)

    return {
        "post_id": post_id,
        "text_output": text_output
    }


# -----------------------------------------
# IMAGE GENERATION JOB
# -----------------------------------------

def generate_image_job(post_id: str, image_prompt: str):

    image_name = f"{post_id}.png"

    result = image_service.generate_image(
        prompt=image_prompt,
        image_name=image_name
    )

    return result


# -----------------------------------------
# RENDER JOB
# -----------------------------------------

def render_post_job(
    post_id: str,
    headline: str,
    caption: str,
    image_path: str
):

    result = render_service.render_post(
        post_id=post_id,
        headline=headline,
        caption=caption,
        image_path=image_path
    )

    return result


# -----------------------------------------
# EVALUATION JOB
# -----------------------------------------

def evaluate_post_job(
    topic: str,
    brand_id: str,
    caption: str
):

    context = rag_service.build_context_block(
        query=topic,
        brand_id=brand_id
    )

    result = evaluation_service.evaluate_post(
        brand_context=context,
        caption=caption
    )

    return result