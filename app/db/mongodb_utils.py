from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class DataBase:
    client: AsyncIOMotorClient = None

db = DataBase()

async def get_database_client() -> AsyncIOMotorClient:
    return db.client

async def connect_to_mongo():
    print(f"Connecting to MongoDB at {settings.MONGODB_CONNECTION_STRING}")
    db.client = AsyncIOMotorClient(settings.MONGODB_CONNECTION_STRING)
    try:
        # The ismaster command is cheap and does not require auth.
        await db.client.admin.command('ismaster')
        print("Successfully connected to MongoDB.")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")

async def close_mongo_connection():
    print("Closing MongoDB connection.")
    db.client.close() 