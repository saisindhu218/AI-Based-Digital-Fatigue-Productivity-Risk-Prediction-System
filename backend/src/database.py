from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None
    
    async def connect(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        self.db = self.client[settings.DATABASE_NAME]
        print("Connected to MongoDB")
        
    async def disconnect(self):
        if self.client:
            self.client.close()
            print("Disconnected from MongoDB")

db = Database()

# Synchronous client for ML service
sync_client = MongoClient(settings.MONGODB_URL)
sync_db = sync_client[settings.DATABASE_NAME]