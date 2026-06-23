from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import initialize_database
from .routes import admin, comments, health, messages, posts, stats


ROOT = Path(__file__).resolve().parents[2]
PUBLIC_FILES = {
    "/": ROOT / "index.html",
    "/index.html": ROOT / "index.html",
    "/styles.css": ROOT / "styles.css",
    "/script.js": ROOT / "script.js",
    "/blog-engine.js": ROOT / "blog-engine.js",
}


def create_app() -> FastAPI:
    initialize_database()

    app = FastAPI(title="Q Blog API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(posts.router)
    app.include_router(comments.router)
    app.include_router(messages.router)
    app.include_router(stats.router)
    app.include_router(admin.router)
    app.mount("/admin", StaticFiles(directory="backend/static/admin", html=True), name="admin")

    @app.get("/{public_path:path}", include_in_schema=False)
    def public_frontend(public_path: str):
        request_path = f"/{public_path}" if public_path else "/"
        file_path = PUBLIC_FILES.get(request_path)
        if file_path and file_path.exists():
            return FileResponse(file_path)
        return FileResponse(PUBLIC_FILES["/"])

    return app


app = create_app()
