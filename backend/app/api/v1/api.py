# backend/app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import assistants, routing, conversations, messages, users
from .endpoints import conversations, chat

api_router = APIRouter()
api_router.include_router(assistants.router, prefix="/assistants", tags=["Assistants"])
api_router.include_router(routing.router, prefix="/routing", tags=["routing"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])  
api_router.include_router(chat.router, tags=["chat"]) 
api_router.include_router(conversations.router)  # 追加
api_router.include_router(messages.router) 
api_router.include_router(users.router)