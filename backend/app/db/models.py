from datetime import datetime
from typing import Optional, List
from beanie import Document
from pydantic import BaseModel, Field


class User(Document):
    email: str
    name: str
    hashed_password: str
    tier: str = "free"  # free, premium, enterprise
    requests_this_month: int = 0
    max_requests: int = 100
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"


class TranscriptionSegment(BaseModel):
    start: float
    end: float
    text: str


class TranscriptionResult(Document):
    user_id: Optional[str] = None
    filename: str
    file_path: str  # S3 path or local path
    text: str
    language: str
    segments: List[TranscriptionSegment] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time: float
    
    class Settings:
        name = "transcriptions"


class SynthesisResult(Document):
    user_id: Optional[str] = None
    text: str
    language: str
    audio_path: str
    slow: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "syntheses"


class UserCreate(BaseModel):
    email: str
    name: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    tier: str
    requests_this_month: int
    max_requests: int
    created_at: datetime


class TranscriptionResponse(BaseModel):
    id: str
    filename: str
    text: str
    language: str
    segments: List[TranscriptionSegment]
    created_at: datetime
    processing_time: float
    
    class Config:
        from_attributes = True
