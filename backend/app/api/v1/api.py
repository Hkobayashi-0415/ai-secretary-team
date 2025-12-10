# app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import assistants, routing, conversations, users, chat, llm

api_router = APIRouter()

# REST
api_router.include_router(assistants.router, prefix="/assistants", tags=["assistants"])
api_router.include_router(routing.router,     prefix="/routing",    tags=["routing"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(users.router,       prefix="/users",      tags=["users"])
api_router.include_router(llm.router,         prefix="/llm",        tags=["llm"])

# WebSocket (例：/api/v1/ws/chat)
api_router.include_router(chat.router,        prefix="/ws",         tags=["chat"])
