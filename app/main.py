from fastapi import FastAPI

from .database import engine, Base
from . import models
from .routers.certificates import router as certificate_router

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Bulk Certificate Generator",
    description="API for generating certificates in bulk",
    version="1.0.0"
)

app.include_router(certificate_router)

@app.get("/")
def root():
    return {
        "message": "Bulk Certificate Generator API is running"
    }