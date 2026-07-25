from __future__ import annotations

import contextlib
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.mcp.server import add_mcp_route, build_session_manager


def create_app() -> FastAPI:
    # Um session manager por app: a instância não pode ser reaproveitada depois
    # que seu `run()` encerra, então criar aqui mantém cada app independente.
    session_manager = build_session_manager()

    @contextlib.asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        # O task group do session manager precisa estar ativo durante toda a
        # vida da app; sem isso a primeira requisição em /mcp estoura em runtime.
        async with session_manager.run():
            yield

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # O cliente MCP lê o id de sessão do header para as requisições seguintes.
        expose_headers=["mcp-session-id"],
    )

    app.include_router(api_router, prefix=settings.api_prefix)
    add_mcp_route(app, session_manager)

    return app


app = create_app()
