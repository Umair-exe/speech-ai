from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(prefix="/api", tags=["health"])


class HealthResponse(BaseModel):
    status: str
    version: str
    message: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify API is running
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        message="Speech API is running"
    )


@router.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "AI Media Detector API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }
