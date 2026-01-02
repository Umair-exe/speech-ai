from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    MONGODB_URI: str = "mongodb://localhost:27017/ai_detector"
    DATABASE_NAME: str = "ai_detector"
    
    # AWS
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_S3_BUCKET: str = "ai-detector-uploads"
    AWS_REGION: str = "us-east-1"
    
    # Azure Speech Services (for emotional TTS)
    AZURE_SPEECH_KEY: str = ""
    AZURE_SPEECH_REGION: str = "eastus"
    
    # JWT
    JWT_SECRET: str = "your-super-secret-jwt-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Model
    MODEL_PATH: str = "./models"
    DEVICE: str = "cpu"
    
    # File Upload
    MAX_FILE_SIZE: int = 104857600  # 100MB
    ALLOWED_IMAGE_TYPES: str = "image/jpeg,image/png,image/gif,image/webp"
    ALLOWED_VIDEO_TYPES: str = "video/mp4,video/quicktime,video/x-msvideo,video/webm"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Features
    ENABLE_BATCH_UPLOAD: bool = True
    ENABLE_VIDEO_PROCESSING: bool = True
    ENABLE_IMAGE_COMPRESSION: bool = True
    
    # Compression
    DEFAULT_COMPRESSION_QUALITY: int = 85
    MAX_COMPRESSION_DIMENSION: int = 4096  # Max width or height
    ALLOWED_OUTPUT_FORMATS: str = "jpeg,jpg,png,webp"
    
    @property
    def allowed_image_types_list(self) -> List[str]:
        return self.ALLOWED_IMAGE_TYPES.split(',')
    
    @property
    def allowed_video_types_list(self) -> List[str]:
        return self.ALLOWED_VIDEO_TYPES.split(',')
    
    @property
    def cors_origins_list(self) -> List[str]:
        return self.CORS_ORIGINS.split(',')
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
