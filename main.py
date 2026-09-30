from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.db.database import init_db
from app.routers import auth, history, pages, planners


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup/shutdown lifecycle.
    """

    init_db()

    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="PocketSmart AI budget and recommendation assistant",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(planners.router)
app.include_router(history.router)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
        "gemini_configured": bool(settings.gemini_api_key),
        "model": settings.gemini_model,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )