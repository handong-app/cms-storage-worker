from fastapi import FastAPI
from app.util.logging_utils import setup_logging
from app.api.router import api_router

setup_logging(level="info")

app = FastAPI(title="CMS Storage Server API")


app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to CMS Storage Server API"}

