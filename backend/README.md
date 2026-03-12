# Brand Post Generator

This repository contains a Python backend service for generating brand-aware social media posts.  The API allows clients to:

1. Create and manage brands.
2. Upload brand documents (PDFs) which are indexed for retrieval.
3. Generate a post based on a topic and a brand.  The pipeline also produces an image, renders a final asset, and evaluates the result.

All data are stored on the local filesystem under the `storage` directory, and documents are ingested into a Qdrant vector database for retrieval augmented generation (RAG).

---

## Prerequisites

Before running the service you will need:

- Python 3.11 or newer installed on your system.
- Git (optional) to clone the repository.
- A Qdrant instance accessible at `http://localhost:6333` (default).  You may run the official Docker image or use a hosted service.
- Redis server running on `localhost:6379` (used for background jobs).
- Environment variables set for API keys:
  - `OPENAI_API_KEY` (OpenAI account key)
  - `REPLICATE_API_TOKEN` (Replicate account token)

All other configuration values are defined in `app/core/config.py` and can be overridden by placing them in a `.env` file at the project root.

---

## Setup

1. Open a terminal in the `backend` directory.
2. Create a virtual environment:
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
4. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. (Optional) install Playwright browsers:
   ```bash
   playwright install
   ```

---

## Running the Application

With the environment active and dependencies installed, start the FastAPI server.

You can run the `uvicorn` command directly. some environments may provide a shorter alias `uv` which behaves the same; the important point is that you are invoking the ASGI server, not `pip`.

```bash
# using the full command name
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# or, if you have an alias, simply
uv app.main:app --reload --host 0.0.0.0 --port 8000
```

The service will be available at `http://localhost:8000`.  A root endpoint returns a simple status message.

### API Endpoints

The service exposes a small set of HTTP routes.  To use the project you generally follow these steps:

1. **Start the server** (see previous section).
2. **Create a brand** – this allocates a new identifier and stores the provided metadata.
   ```bash
   curl -X POST http://localhost:8000/brands \
     -H "Content-Type: application/json" \
     -d '{"name":"Acme","description":"Gadgets for everyone","tone":"friendly"}'
   ```
   The response body will look like:
   ```json
   {
     "brand_id": "<uuid>",
     "name": "Acme",
     "description": "Gadgets for everyone",
     "tone": "friendly"
   }
   ```
3. **List brands** – verify that the brand was created.
   ```bash
   curl http://localhost:8000/brands
   ```
   Returns an array of brand objects.
4. **Retrieve a single brand** – fetch metadata by id.
   ```bash
   curl http://localhost:8000/brands/<brand_id>
   ```
5. **Upload a document** for a brand.  This will store the PDF and begin ingestion.
   ```bash
   curl -X POST http://localhost:8000/brands/<brand_id>/documents \
     -F "file=@path/to/file.pdf"
   ```
   The response contains details including the path on disk and ingestion results.
6. **Generate a post** – once you have uploaded any necessary documents and allowed ingestion to complete, you can request a social media post.
   ```bash
   curl -X POST http://localhost:8000/generate \
     -H "Content-Type: application/json" \
     -d '{"brand_id":"<brand_id>","topic":"launching our new product"}'
   ```
   The JSON response includes the generated text, image information, rendered asset path, and an evaluation summary.

Each of the above steps is also available through the automatically generated Swagger UI at `http://localhost:8000/docs`.  You may use the UI to experiment with parameters and view request/response schemas.

---

## Usage Notes

1. Ensure Qdrant and Redis are running before uploading documents or generating posts.
2. Uploaded PDFs are processed to extract text, filter noise, chunk content, and index it for RAG.
3. Generated posts use the OpenAI API; usage may incur costs.
4. Images are produced by the Replicate API and stored locally.

---

## Development

- Code is organized under `app/`.  FastAPI routers live in `app/api`, services in `app/services`, and vector logic under `app/vector`.
- Configuration settings reside in `app/core/config.py`.
- Static prompts live in `app/prompts` and the HTML template in `app/templates`.

To run tests or add new features, modify the appropriate modules and restart the server.

---

## License

This project does not include a license file.  Add one if you plan to share or distribute the code.
