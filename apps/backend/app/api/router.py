from fastapi import APIRouter

from app.api.routes import agui, chat, conversations, health, mcp_apps

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(chat.router, tags=["chat"])
api_router.include_router(conversations.router, tags=["conversations"])
api_router.include_router(agui.router, tags=["agui"])
api_router.include_router(mcp_apps.router, tags=["mcp-apps"])
