"""
Render Service

Responsible for rendering social media assets
using HTML templates and Playwright.

Pipeline:

HTML Template
     ↓
Inject text + image
     ↓
Playwright Headless Browser
     ↓
Screenshot → PNG
"""

from pathlib import Path
from typing import Dict

from playwright.sync_api import sync_playwright

from app.services.storage_service import storage_service


class RenderService:
    """
    Handles rendering of social media assets.
    """

    def __init__(self):

        # Template location
        self.template_path = Path("backend/app/templates/post_template.html")

    # -----------------------------------------
    # LOAD TEMPLATE
    # -----------------------------------------

    def load_template(self) -> str:

        if not self.template_path.exists():
            raise FileNotFoundError(
                f"Template not found: {self.template_path}"
            )

        return self.template_path.read_text()

    # -----------------------------------------
    # BUILD HTML
    # -----------------------------------------

    def build_html(self, headline: str, caption: str, image_path: str) -> str:
        """
        Inject content into HTML template.
        """

        template = self.load_template()

        html = template.format(
            headline=headline,
            caption=caption,
            image_path=image_path
        )

        return html

    # -----------------------------------------
    # RENDER IMAGE
    # -----------------------------------------

    def render_post(
        self,
        post_id: str,
        headline: str,
        caption: str,
        image_path: str
    ) -> Dict:
        """
        Render final social media asset using Playwright.
        """

        html = self.build_html(
            headline=headline,
            caption=caption,
            image_path=image_path
        )

        post_folder = storage_service.create_post_folder(post_id)

        html_file = post_folder / "render.html"
        output_image = post_folder / "post.png"

        # Save temporary HTML file
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html)

        with sync_playwright() as p:

            browser = p.chromium.launch()

            page = browser.new_page(
                viewport={"width": 1080, "height": 1080}
            )

            page.goto(f"file://{html_file.resolve()}")

            page.screenshot(path=str(output_image))

            browser.close()

        return {
            "post_id": post_id,
            "image_path": str(output_image)
        }


render_service = RenderService()