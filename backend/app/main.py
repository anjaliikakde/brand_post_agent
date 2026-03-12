from fastapi import FastAPI

from app.api import brands
from app.api import documents
from app.api import posts

from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(
    title="Brand AI Post Generator",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brands.router)
app.include_router(documents.router)
app.include_router(posts.router)


@app.get("/")
def root():

    return {
        "message": "Brand Post Generator API running"
    }