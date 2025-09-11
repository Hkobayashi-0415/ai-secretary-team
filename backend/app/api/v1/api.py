# backend/app/api/v1/api.py
from app.api.v1.endpoints import assistants, routing
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(assistants.router, prefix="/assistants", tags=["Assistants"])
api_router.include_router(routing.router, prefix="/routing", tags=["routing"])
