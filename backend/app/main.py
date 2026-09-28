from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Fluid Controls RFQ Management and Quotation Automation API",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health/live", tags=["System"])
def health_live():
    return {
        "status": "ok",
        "service": "fluid-controls-rfq-backend",
    }


@app.get("/health/ready", tags=["System"])
def health_ready():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "ready",
        "database": "ok",
    }


app.include_router(
    api_router,
    prefix="/api/v1",
)
