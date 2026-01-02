from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.db.database import connect_to_mongo, close_mongo_connection
from app.routes import speech, health, compression, translation, ocr, ai_detection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    # await connect_to_mongo()
    yield
    # Shutdown
    # await close_mongo_connection()


# Create FastAPI app
app = FastAPI(
    title="Speech API",
    description="Convert speech to text and text to speech using AI models",
    version="1.0.0",
    # lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(speech.router)
app.include_router(compression.router)
app.include_router(translation.router)
app.include_router(ocr.router)
app.include_router(ai_detection.router, prefix="/api/ai-detection", tags=["ai-detection"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
