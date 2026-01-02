from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from app.db.models import User, TranscriptionResult, SynthesisResult


class Database:
    client: AsyncIOMotorClient = None


db = Database()


async def connect_to_mongo():
    """Connect to MongoDB and initialize Beanie"""
    db.client = AsyncIOMotorClient(settings.MONGODB_URI)
    await init_beanie(
        database=db.client[settings.DATABASE_NAME],
        document_models=[User, TranscriptionResult, SynthesisResult]
    )
    print("✅ Connected to MongoDB")


async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        print("❌ Disconnected from MongoDB")
