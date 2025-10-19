# backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.logging import get_logger

# Import models so metadata (tables) are registered with SQLAlchemy
from app.models import models as _models  # noqa: F401
from app.models import phase2_models as _phase2_models  # noqa: F401

app = FastAPI(title="AI Secretary Team API", version="1.0.0")
logger = get_logger("app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    # Log HTTP exceptions with structured context
    if 400 <= exc.status_code < 500:
        logger.warning("HTTPException", status_code=exc.status_code, detail=exc.detail)
    else:
        logger.error("HTTPException", status_code=exc.status_code, detail=exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, exc: Exception):
    # Fallback for unexpected errors
    logger.error("Unhandled exception", error=str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


# v1 routes
app.include_router(api_router, prefix="/api/v1")
