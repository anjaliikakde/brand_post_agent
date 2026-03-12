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

        # self.prompt_path = Path("backend/app/prompts/caption_prompt.txt")
        self.prompt_path = Path(__file__).parent.parent / "prompts" / "caption_prompt.txt"

        self.model = "gpt-4o-mini"

    # ----------------------------------------
    # PROMPT LOADING
    # ----------------------------------------

    def load_prompt_template(self) -> str:
        """
        Load caption prompt template from file.
        """

        if not self.prompt_path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {self.prompt_path}"
            )

        return self.prompt_path.read_text()

    # ----------------------------------------
    # BUILD PROMPT
    # ----------------------------------------

    def build_prompt(self, topic: str, brand_id: str) -> str:
        """
        Construct prompt using RAG context.
        """

        context = rag_service.build_context_block(topic, brand_id)

        template = self.load_prompt_template()

        prompt = template.format(
            brand_context=context,
            topic=topic,
        )

        return prompt

    # ----------------------------------------
    # GENERATE TEXT
    # ----------------------------------------

    def generate_post(self, topic: str, brand_id: str) -> Dict:
        """
        Generate social media post text.
        """

        prompt = self.build_prompt(topic, brand_id)

        # response = self.client.chat.completions.create(
        #     model=self.model,
        #     messages=[
        #         {
        #             "role": "system",
        #             "content": "You are a brand-aware social media copywriter."
        #         },
        #         {
        #             "role": "user",
        #             "content": prompt
        #         }
        #     ],
        #     temperature=0.7
        # )
        
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
            "brand_id": brand_id,
            "topic": topic
        }


generation_service = GenerationService()