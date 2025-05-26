import logging
from fastapi import FastAPI


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


app = FastAPI(title="CMS Storage Server API")




@app.get("/")
def root():
    return {"message": "Welcome to CMS Storage Server API"}

