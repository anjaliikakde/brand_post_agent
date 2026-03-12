# Brand Post Generator

A full-stack application that generates brand-aware social media posts. Upload a brand document, choose a topic, and the app produces a headline, caption, and a rendered post image.

---

## Tech Stack

- Backend: FastAPI, Python
- Vector DB: Qdrant
- LLM: OpenAI gpt-4o-mini
- Image generation: Replicate (Flux Dev)
- Browser rendering: Playwright
- Frontend: React + Vite
- Package manager: uv

---

## Project Structure

```
brand_post_agent/
    backend/
        app/
            api/            route handlers
            services/       business logic
            core/           config and settings
            prompts/        LLM prompt templates
            templates/      HTML post template
            outputs/        generated post PNGs (auto-created)
        storage/            uploaded docs and generated images
    frontend/
        src/
            App.jsx
```

---

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- uv: https://docs.astral.sh/uv/getting-started/installation/
- Docker Desktop (to run Qdrant)
- OpenAI API key: https://platform.openai.com
- Replicate API token: https://replicate.com

---

## Setup

### Step 1 - Start Qdrant

```bash
docker pull qdrant/qdrant
docker run -p 6333:6333 qdrant/qdrant
```

Leave this terminal running.

---

### Step 2 - Configure environment variables

Inside the `backend` folder, create a `.env` file:

```
OPENAI_API_KEY=your_openai_key_here
REPLICATE_API_TOKEN=your_replicate_token_here
QDRANT_URL=http://localhost:6333
```

---

### Step 3 - Install backend dependencies

```bash
cd backend
uv venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Mac / Linux
uv pip install -r requirements.txt
```

---

### Step 4 - Install Playwright browser

Run once after activating the virtual environment:

```bash
python -m playwright install chromium
```

---

### Step 5 - Start the backend

```bash
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000
API docs available at http://localhost:8000/docs

---

### Step 6 - Install frontend dependencies

Open a new terminal:

```bash
cd frontend
npm install
```

---

### Step 7 - Start the frontend

```bash
npm run dev
```

Frontend runs at http://localhost:5173

---

## Using the App

1. Open http://localhost:5173
2. Upload a brand document (TXT, PDF, or DOCX)
3. Fill in the Brand Voice box with your brand tone and audience
4. Enter a topic such as "Product launch" or "Brand story"
5. Click Generate

The app returns a rendered post image with headline and caption.

---

## Troubleshooting

**Qdrant connection error**
Make sure Docker is running and the Qdrant container is up on port 6333 before starting the backend.

**POST /generate returns 500**
Check the uvicorn terminal for the full error. Common causes are a missing API key in `.env` or Replicate timing out.

**Generated image is black**
The image path is not resolving correctly in Playwright. Confirm `render_service.py` converts the image path to a `file://` URL using `Path.as_uri()`.

**uv command not found**

```bash
# Mac / Linux
curl -Lsf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## Notes

- The `outputs` folder is created automatically on first run.
- Replicate image generation with flux-dev takes 20 to 40 seconds. This is expected.
- All generated images and posts are stored locally under `storage/`.