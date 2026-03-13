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

# Anchored to THIS file's location — works regardless of where uvicorn is launched from
BASE_DIR = Path(__file__).resolve().parent.parent  # → /app

# Posts save here — must match the directory FastAPI mounts at /outputs
OUTPUTS_DIR = BASE_DIR / "outputs"


class RenderService:
    """
    Handles rendering of social media assets.
    """

    def __init__(self):
        self.template_path = BASE_DIR / "templates" / "post_template.html"
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # -----------------------------------------
    # LOAD TEMPLATE
    # -----------------------------------------

    def load_template(self) -> str:

        if not self.template_path.exists():
            raise FileNotFoundError(
                f"Template not found: {self.template_path}"
            )

        return self.template_path.read_text(encoding="utf-8")

    # -----------------------------------------
    # BUILD HTML
    # -----------------------------------------

    def build_html(self, headline: str, caption: str, image_path: str) -> str:
        """
        Inject content into HTML template.
        image_path must be a file:// URL so Playwright can load it.
        """

        template = self.load_template()

        html = (
            template
            .replace("{{headline}}", headline)
            .replace("{{caption}}", caption)
            .replace("{{image_path}}", image_path)
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
        image_path: str,
    ) -> Dict:
        """
        Render final social media asset using Playwright.

        Saves to app/outputs/{post_id}/post.png — served by FastAPI at
        GET /outputs/{post_id}/post.png
        """

        # Fix 1 — save to app/outputs/{post_id}/ not storage/posts/
        # This is the directory FastAPI mounts at /outputs
        post_folder = OUTPUTS_DIR / post_id
        post_folder.mkdir(parents=True, exist_ok=True)

        # Fix 2 — convert raw Windows path to file:// URL so Playwright
        # can load the image inside the HTML template
        image_file_url = Path(image_path).resolve().as_uri()
        # e.g. file:///E:/Superteamsai.../storage/images/abc123.png

        html = self.build_html(
            headline=headline,
            caption=caption,
            image_path=image_file_url,
        )

        html_file = post_folder / "render.html"
        output_image = post_folder / "post.png"

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html)

        with sync_playwright() as p:

            browser = p.chromium.launch()

            page = browser.new_page(
                viewport={"width": 1080, "height": 1080}
            )

            page.goto(
                f"file://{html_file.resolve()}",
                wait_until="networkidle",
            )

            page.screenshot(
                path=str(output_image),
                full_page=False,
            )

            browser.close()

        return {
            "post_id": post_id,
            "output_path": str(output_image),      # fixed: was "image_path"
            "rendered_url": f"/outputs/{post_id}/post.png",
        }
        


render_service = RenderService()