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
- Docker Desktop (to run Qdrant, or full app via Docker Compose)
- OpenAI API key: https://platform.openai.com
- Replicate API token: https://replicate.com

---

## Option A — Run Manually (Recommended for development)

### Step 1 - Start Qdrant

```bash
docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant
```

Leave this terminal running. Qdrant dashboard is available at http://localhost:6333/dashboard

---

### Step 2 - Configure environment variables

Inside the `backend` folder, create a `.env` file:

```
OPENAI_API_KEY=your_openai_key_here
REPLICATE_API_TOKEN=your_replicate_token_here
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=brand_knowledge
CHUNK_SIZE=1500
CHUNK_OVERLAP=200
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

## Option B — Run with Docker Compose

This starts Qdrant, the FastAPI backend, and the React frontend together with a single command.

### Step 1 - Configure environment variables

Inside the `backend` folder, create a `.env` file:

```
OPENAI_API_KEY=your_openai_key_here
REPLICATE_API_TOKEN=your_replicate_token_here
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=brand_knowledge
CHUNK_SIZE=1500
CHUNK_OVERLAP=200
```

Do not change `QDRANT_URL` here. Docker Compose overrides it internally to point to the Qdrant container.

---

### Step 2 - Add host config to Vite

In `frontend/vite.config.js`, make sure the dev server is exposed to Docker:

```js
export default {
  server: {
    host: '0.0.0.0',
    port: 5173,
  }
}
```

---

### Step 3 - Build and start all services

From the project root (where `docker-compose.yml` lives):

```bash
docker-compose up --build
```

First run takes 5 to 10 minutes. It downloads base images, installs all Python dependencies, and downloads the Playwright Chromium browser.

After the first build, subsequent starts are fast:

```bash
docker-compose up
```

---

### Step 4 - Access the app

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| Qdrant dashboard | http://localhost:6333/dashboard |

---

### Docker Compose commands

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop all services (data is preserved)
docker-compose down

# Stop and delete all data including Qdrant vectors
docker-compose down -v

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

### Data storage with Docker

All data is stored locally on your machine, not inside containers:

- `qdrant_storage/` — Qdrant vectors (auto-created in project root)
- `backend/storage/` — uploaded documents and generated images
- `backend/app/outputs/` — rendered post PNGs

Data survives `docker-compose down`. Only `docker-compose down -v` deletes it.

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

**Docker build fails with TLS handshake timeout**
This is a network issue, not a code issue. Try the following:
- Open Docker Desktop → Settings → Docker Engine
- Add DNS servers to the config:
  ```json
  {
    "dns": ["8.8.8.8", "8.8.4.4"]
  }
  ```
- Click Apply and Restart
- Try `docker-compose up --build` again

If on a corporate or college network, switch to a home network or mobile hotspot.

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
- Each browser session gets a unique brand ID stored in `localStorage`. This scopes all uploaded documents and RAG retrieval to your session. If you want to start fresh with a new brand, run `localStorage.removeItem("session_brand_id")` in the browser console and refresh.