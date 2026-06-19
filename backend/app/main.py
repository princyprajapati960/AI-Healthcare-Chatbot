from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.database.connection import init_db
from backend.app.routes import auth, chat, user, voice, cache
from backend.app.services.triage_ml import load_model
from backend.app.services.cache_manager import cache_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    load_model()
    await cache_manager.connect()
    yield
    # Shutdown
    await cache_manager.disconnect()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(chat.router)
app.include_router(voice.router)
app.include_router(cache.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name}
