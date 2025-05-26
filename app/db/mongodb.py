from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from app.db.mongodb_utils import get_database_client

async def get_database() -> AsyncIOMotorDatabase:
    client = await get_database_client()
    if client is None:
        raise RuntimeError("Database client not initialized. Ensure connect_to_mongo() was called.")
    return client[settings.DATABASE_NAME] 