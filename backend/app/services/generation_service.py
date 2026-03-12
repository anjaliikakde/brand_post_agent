"""
Generation Service

Responsible for generating brand-aware social media
text content using OpenAI.

Uses:
- RAG context
- prompt templates stored in /prompts
"""

from pathlib import Path
from typing import Dict

from openai import OpenAI

from app.core.config import settings
from app.services.rag_service import rag_service


class GenerationService:
    """
    Handles caption generation using OpenAI.
    """

    def __init__(self):

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

        self.prompt_path = Path(__file__).parent.parent / "prompts" / "caption_prompt.txt"

        self.model = "gpt-4o-mini"

    # ----------------------------------------
    # PROMPT LOADING
    # ----------------------------------------

    def load_prompt_template(self) -> str:

        if not self.prompt_path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {self.prompt_path}"
            )

        return self.prompt_path.read_text(encoding="utf-8")

    # ----------------------------------------
    # BUILD PROMPT
    # ----------------------------------------

    def build_prompt(self, topic: str, brand_id: str, brand_context: str = "") -> str:
        """
        Construct prompt using RAG context from Qdrant.
        Falls back to brand_context string if RAG returns nothing.
        """

        # Try to get context from vector DB first
        rag_context = rag_service.build_context_block(topic, brand_id)

        # Fall back to the raw brand_context the user typed if RAG is empty
        context = rag_context if rag_context else brand_context

        template = self.load_prompt_template()

        # Use replace() — str.format() breaks on any { } in the template
        prompt = (
            template
            .replace("{{brand_context}}", context)
            .replace("{{topic}}", topic)
        )

        return prompt

    # ----------------------------------------
    # GENERATE TEXT
    # ----------------------------------------

    def generate_post(self, topic: str, brand_id: str, brand_context: str = "") -> Dict:
        """
        Generate social media post text.
        """

        prompt = self.build_prompt(
            topic=topic,
            brand_id=brand_id,
            brand_context=brand_context
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert brand marketing copywriter who strictly follows provided brand context."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.6,
            max_tokens=500
        )

        content = response.choices[0].message.content

        return {
            "text_output": content,
            "topic": topic
        }


generation_service = GenerationService()