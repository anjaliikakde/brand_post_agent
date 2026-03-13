"""
Posts API

Handles the full post generation pipeline:
1. Generate text via RAG + LLM
2. Generate image prompt via LLM
3. Generate image via Replicate
4. Render final post via Playwright
5. Evaluate post quality via LLM-as-judge
"""

import re
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from typing import List

from openai import OpenAI
from app.core.config import settings
from app.services.generation_service import generation_service
from app.services.image_service import image_service
from app.services.render_service import render_service
from app.services.evaluation_service import evaluation_service
from app.services.rag_service import rag_service


router = APIRouter()
_openai = OpenAI(api_key=settings.OPENAI_API_KEY)

# Bug 10 fix — read image prompt from file
IMAGE_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "image_prompt.txt"


class PostRequest(BaseModel):
    brand_id: str
    brand_context: str
    topic: str
    document_ids: List[str] = []


def clean_text(text: str) -> str:
    """
    Strip markdown bold/italic markers and label prefixes the LLM adds.
    e.g. **Headline:** "Real Users..." → Real Users...
    """
    text = re.sub(r"\*\*[^*]+:\*\*\s*", "", text)
    text = text.replace("**", "")
    text = text.strip().strip('"').strip("'")
    return text.strip()


def generate_image_prompt(
    brand_context: str,
    topic: str,
    headline: str,
) -> str:
    """
    Ask the LLM to write a Replicate-optimized visual prompt.
    Reads system prompt from image_prompt.txt if available.
    """

    # Bug 10 fix — use image_prompt.txt instead of hardcoded string
    if IMAGE_PROMPT_PATH.exists():
        system_content = IMAGE_PROMPT_PATH.read_text(encoding="utf-8").strip()
    else:
        system_content = (
            "You write image generation prompts for social media posts. "
            "Describe a photographic or illustrated scene that visually represents "
            "the brand and topic. Never include text, words, letters, or signs in the scene. "
            "Keep it under 40 words. Be specific about lighting, mood, and subject."
        )

    response = _openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_content,
            },
            {
                "role": "user",
                "content": (
                    f"Brand context: {brand_context}\n"
                    f"Topic: {topic}\n"
                    f"Post headline: {headline}\n\n"
                    "Write a visual image prompt for this post. No text in the image."
                ),
            },
        ],
        temperature=0.7,
        max_tokens=80,
    )
    return response.choices[0].message.content.strip()


@router.post("/generate")
def generate_post(request: PostRequest):

    post_id = str(uuid.uuid4())

    # --------------------------------------------------
    # Step 1 — Generate headline + caption via RAG + LLM
    # --------------------------------------------------
    try:
        generation = generation_service.generate_post(
            topic=request.topic,
            brand_id=request.brand_id,
            brand_context=request.brand_context,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text generation failed: {e}")

    text_output = generation["text_output"]

    # --------------------------------------------------
    # Step 2 — Parse headline + caption from LLM output
    # --------------------------------------------------
    headline = ""
    caption = ""

    lines = [l.strip() for l in text_output.strip().splitlines() if l.strip()]

    for line in lines:
        if re.match(r"[\*]*headline[\*]*\s*:", line, re.IGNORECASE):
            headline = clean_text(re.sub(r"(?i)[\*]*headline[\*]*\s*:", "", line))
        elif re.match(r"[\*]*caption[\*]*\s*:", line, re.IGNORECASE):
            caption = clean_text(re.sub(r"(?i)[\*]*caption[\*]*\s*:", "", line))

    # Bug 5 fix — skip preamble lines before picking headline fallback
    if not headline and lines:
        preamble = [
            r"^here (is|are)",
            r"^sure",
            r"^of course",
            r"^below",
            r"^certainly",
        ]
        for line in lines:
            if not any(re.match(p, line, re.IGNORECASE) for p in preamble):
                headline = clean_text(line)
                break
        remaining = [l for l in lines if l != headline]
        caption = clean_text(" ".join(remaining)) if remaining else headline

    if not caption:
        caption = text_output.strip()

    # --------------------------------------------------
    # Step 3 — Generate a VISUAL image prompt via LLM
    # --------------------------------------------------
    try:
        image_prompt = generate_image_prompt(
            brand_context=request.brand_context,
            topic=request.topic,
            headline=headline,
        )
    except Exception:
        image_prompt = (
            f"Professional lifestyle photography representing {request.topic}, "
            "modern workspace, soft natural lighting, cinematic composition, "
            "no text, no words"
        )

    # --------------------------------------------------
    # Step 4 — Generate image via Replicate
    # --------------------------------------------------
    try:
        image = image_service.generate_image(
            prompt=image_prompt,
            image_name=f"{post_id}.png",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {e}")

    # --------------------------------------------------
    # Step 5 — Render final post PNG via Playwright
    # --------------------------------------------------
    try:
        rendered = render_service.render_post(
            post_id=post_id,
            headline=headline,
            caption=caption,
            image_path=image["image_path"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Render failed: {e}")

    # --------------------------------------------------
    # Step 6 — Build context for evaluation
    # --------------------------------------------------
    rag_context = rag_service.build_context_block(
        query=request.topic,
        brand_id=request.brand_id,
    )
    eval_context = rag_context if rag_context else request.brand_context

    # --------------------------------------------------
    # Step 7 — Evaluate post quality (non-fatal)
    # --------------------------------------------------
    try:
        evaluation = evaluation_service.evaluate_post(
            brand_context=eval_context,
            caption=caption,
        )
    except Exception:
        evaluation = {
            "evaluation": '{"tone": 0, "accuracy": 0, "engagement": 0, "notes": "Evaluation unavailable"}'
        }

    # Bug 7 fix — return rendered post URL so frontend can load it
    return {
        "post_id": post_id,
        "headline": headline,
        "caption": caption,
        "image_path": image["image_path"],
        "rendered_post_url": f"/outputs/{post_id}/post.png",
        "evaluation": evaluation["evaluation"],
    }