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
import json

from openai import OpenAI

from app.core.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent


class EvaluationService:
    """
    Evaluates generated social media posts.
    """

    def __init__(self):

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

        self.prompt_path = BASE_DIR / "prompts" / "judge_prompt.txt"

        self.model = "gpt-4o-mini"

    # -----------------------------------------
    # LOAD JUDGE PROMPT
    # -----------------------------------------

    def load_prompt_template(self) -> str:

        if not self.prompt_path.exists():
            raise FileNotFoundError(
                f"Judge prompt not found: {self.prompt_path}"
            )

        return self.prompt_path.read_text(encoding="utf-8")

    # -----------------------------------------
    # BUILD JUDGE PROMPT
    # -----------------------------------------

    def build_prompt(
        self,
        brand_context: str,
        caption: str
    ) -> str:

        template = self.load_prompt_template()

        # Use replace() — str.format() chokes on the JSON braces in the prompt
        prompt = (
            template
            .replace("{{context}}", brand_context)
            .replace("{{caption}}", caption)
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
                    "content": "You are an expert marketing reviewer. Respond with valid JSON only. No markdown, no explanation."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_tokens=300
        )
        
        result = response.choices[0].message.content.strip()

        # Bug 2 fix — verify GPT returned JSON, don't trust it blindly
        try:
            clean = result.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean)
            return {"evaluation": json.dumps(parsed)}
        except json.JSONDecodeError:
            return {
                "evaluation": json.dumps({
                    "tone": 0,
                    "accuracy": 0,
                    "engagement": 0,
                    "notes": f"Evaluation parsing failed. Raw: {result[:200]}"
                })
            }



evaluation_service = EvaluationService()