# Brand Post Generator

Brand Post Generator is a full-stack application that helps create brand-aware social media posts. It combines a Python FastAPI backend with a React frontend.

The system allows you to:
- Create and manage brands with specific tone and description.
- Upload brand documents (PDFs) which are indexed for retrieval.
- Generate social media posts based on a topic and brand context.
- View generated images, rendered assets, and evaluations from an AI judge.

All data is stored on the local filesystem under the `storage` directory, and documents are ingested into a Qdrant vector database for retrieval augmented generation (RAG).

---

## Project Structure

```
.
├── backend/              # Python FastAPI service
│   ├── app/
│   │   ├── api/          # API route handlers
│   │   ├── services/     # Business logic
│   │   ├── core/         # Configuration
│   │   ├── prompts/      # LLM prompt templates
│   │   ├── templates/    # HTML templates
│   │   └── vector/       # Vector DB operations
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── README.md
├── frontend/             # React + Vite
│   ├── src/
│   ├── package.json
│   └── README.md
└── README.md             # This file
```

---

## Prerequisites

Before running the application you will need:

- Python 3.11 or newer installed on your system.
- Node.js and npm installed on your system.
- A Qdrant instance accessible at `http://localhost:6333` (default).  You may run the official Docker image or use a hosted service.
- Redis server running on `localhost:6379` (used for background jobs).
- Environment variables set for API keys:
  - `OPENAI_API_KEY` (OpenAI account key)
  - `REPLICATE_API_TOKEN` (Replicate account token)

---

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a Python virtual environment:
   ```powershell
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - On Windows PowerShell:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - On Windows Command Prompt:
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. Install Python dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Install Playwright browsers for rendering:
   ```bash
   playwright install
   ```

6. Create a `.env` file in the backend directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_key
   REPLICATE_API_TOKEN=your_replicate_token
   QDRANT_URL=http://localhost:6333
   REDIS_URL=redis://localhost:6379
   ```

---

## Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node.js dependencies:
   ```bash
   npm install
   ```

---

## Running the Application

You need to run the backend and frontend in separate terminal windows.

### Terminal 1: Start the Backend

1. Navigate to the backend directory and activate the virtual environment:
   ```bash
   cd backend
   .venv\Scripts\Activate.ps1      # Windows PowerShell
   # or
   source .venv/bin/activate       # macOS/Linux
   ```

2. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   The backend API will be available at `http://localhost:8000`

### Terminal 2: Start the Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```
   
   The frontend will be available at `http://localhost:5173`

---

## Using the Application

### Via Frontend UI

Once both servers are running, open your browser to `http://localhost:5173` to use the graphical interface. The UI guides you through the workflow of creating brands, uploading documents, and generating posts.

### Via API

You can also interact with the backend API directly. Here is the typical workflow:

#### Step 1: Create a Brand

```bash
curl -X POST http://localhost:8000/brands \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corp",
    "description": "Leading innovator in technology",
    "tone": "professional and friendly"
  }'
```

Copy the returned `brand_id` for use in subsequent requests.

#### Step 2: List All Brands

```bash
curl http://localhost:8000/brands
```

#### Step 3: Get a Single Brand

```bash
curl http://localhost:8000/brands/<brand_id>
```

#### Step 4: Upload a Brand Document

```bash
curl -X POST http://localhost:8000/brands/<brand_id>/documents \
  -F "file=@/path/to/document.pdf"
```

The ingestion process will extract text, normalize it, filter noise, chunk it, and index it for retrieval.

#### Step 5: Generate a Post

Once documents are ingested, generate a post on a specific topic:

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "brand_id": "<brand_id>",
    "topic": "launching our new product line"
  }'
```

The response includes:
- Generated text caption
- Image generated by Replicate
- Rendered final asset path
- Evaluation from the AI judge

### API Documentation

The backend provides interactive API documentation at `http://localhost:8000/docs` (Swagger UI). Use this to explore all endpoints and test them directly in your browser.

---

## Important Notes

1. Ensure Qdrant and Redis are running before uploading documents or generating posts.
2. Uploaded PDFs are processed to extract text, filter noise, chunk content, and index it for RAG.
3. Generated posts use the OpenAI API; usage may incur costs based on your OpenAI plan.
4. Images are produced by the Replicate API; API costs apply.
5. All generated images and posts are stored locally in the `storage` directory.

---

## Backend Architecture

The backend is organized as follows:

- `app/api/` - FastAPI route handlers for brands, documents, and posts
- `app/services/` - Business logic services for brand management, document ingestion, generation, evaluation, and rendering
- `app/core/config.py` - Global configuration and environment variable loading
- `app/prompts/` - Template files for LLM prompts
- `app/templates/` - HTML templates for rendering final assets
- `app/vector/` - Qdrant vector database operations and hybrid search

For more details, see `backend/README.md`.

---

## Frontend Architecture

The frontend is a React application built with Vite. It provides:

- Brand creation and management interface
- Document upload form
- Post generation workflow
- Results display with images and evaluations

For more details, see `frontend/README.md`.

---

## Troubleshooting

**Backend fails to start:**
- Verify Python 3.11 or newer is installed
- Ensure virtual environment is activated
- Check that all dependencies in `requirements.txt` are installed

**Frontend fails to start:**
- Verify Node.js and npm are installed
- Ensure all dependencies in `package.json` are installed
- Check that port 5173 is available

**API calls return errors:**
- Verify backend is running at `http://localhost:8000`
- Check API keys are correctly set in `.env` file
- Ensure Qdrant and Redis are running
- Check the Swagger UI at `http://localhost:8000/docs` for detailed error messages

---

## License

This project does not include a license file.


