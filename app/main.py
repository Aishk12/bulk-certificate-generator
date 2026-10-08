from fastapi import FastAPI

from app.database.database import Base, engine
from app.database import models
from app.api.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bulk Certificate Generator",
    description="API for generating certificates in bulk",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Bulk Certificate Generator API is running"
    }