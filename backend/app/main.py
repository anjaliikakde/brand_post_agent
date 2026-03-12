from fastapi import FastAPI

from app.api import brands
from app.api import documents
from app.api import posts


app = FastAPI(
    title="Brand AI Post Generator",
    version="1.0"
)


app.include_router(brands.router)
app.include_router(documents.router)
app.include_router(posts.router)


@app.get("/")
def root():

    return {
        "message": "Brand Post Generator API running"
    }