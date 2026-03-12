"""
Evaluation Service

Uses OpenAI to evaluate generated posts using
an LLM-as-a-judge pattern.

The judge evaluates:

- Brand tone alignment
- Marketing quality
- Hallucination risk
"""

from pathlib import Path
from typing import Dict

from openai import OpenAI

from app.core.config import settings


class EvaluationService:
    """
    Evaluates generated social media posts.
    """

    def __init__(self):

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

        self.prompt_path = Path("backend/app/prompts/judge_prompt.txt")

        self.model = "gpt-4o-mini"

    # -----------------------------------------
    # LOAD JUDGE PROMPT
    # -----------------------------------------

    def load_prompt_template(self) -> str:

        if not self.prompt_path.exists():
            raise FileNotFoundError(
                f"Judge prompt not found: {self.prompt_path}"
            )

        return self.prompt_path.read_text()

    # -----------------------------------------
    # BUILD JUDGE PROMPT
    # -----------------------------------------

    def build_prompt(
        self,
        brand_context: str,
        caption: str
    ) -> str:

        template = self.load_prompt_template()

        prompt = template.format(
            brand_context=brand_context,
            caption=caption,
        )

        return prompt

    # -----------------------------------------
    # RUN EVALUATION
    # -----------------------------------------

    def evaluate_post(
        self,
        brand_context: str,
        caption: str
    ) -> Dict:

        prompt = self.build_prompt(
            brand_context=brand_context,
            caption=caption
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert marketing reviewer."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_tokens=300
        )

        result = response.choices[0].message.content

        return {
            "evaluation": result
        }


evaluation_service = EvaluationService()