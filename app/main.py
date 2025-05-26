from fastapi import FastAPI
from app.util.logging_utils import setup_logging

setup_logging(level="info")

app = FastAPI(title="CMS Storage Server API")




@app.get("/")
def root():
    return {"message": "Welcome to CMS Storage Server API"}

