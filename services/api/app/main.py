from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin_router import router as admin_router
from app.api.app_router import router as app_router
from app.api.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="Heaver Energy API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5173",
            "http://localhost:5173",
            "https://helicloud.cn",
            "https://www.helicloud.cn",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router, prefix="/api")
    app.include_router(app_router, prefix="/api")
    app.include_router(admin_router, prefix="/api")
    return app


app = create_app()

