from motor.motor_asyncio import AsyncIOMotorClient
from src.config import settings
from datetime import datetime

class Database:
    client = None
    db = None
    
    async def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            print(f"🔗 Connecting to MongoDB Atlas...")
            
            # Get connection string from settings
            connection_string = settings.MONGODB_URL
            db_name = settings.DATABASE_NAME
            
            print(f"📊 Database name: {db_name}")
            
            # Create client
            self.client = AsyncIOMotorClient(
                connection_string,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            
            # Test connection
            await self.client.admin.command('ping')
            print("✅ MongoDB Atlas ping successful")
            
            # Get database
            self.db = self.client[db_name]
            
            # Test by listing collections
            collections = await self.db.list_collection_names()
            print(f"✅ Connected to database. Collections: {collections}")
            
            # Create indexes
            try:
                await self.db.users.create_index("email", unique=True)
                print("✅ Created email index")
            except Exception as e:
                print(f"ℹ️ Email index may already exist: {e}")
            
            print(f"✅ Database connection successful")
            return True
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            self.client = None
            self.db = None
            return False
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("✅ Database connection closed")
            self.client = None
            self.db = None

# Create global instance
db = Database()