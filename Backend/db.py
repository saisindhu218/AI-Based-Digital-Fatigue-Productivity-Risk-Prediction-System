from pymongo import MongoClient
import certifi

# MongoDB Atlas Connection
MONGO_URI = "mongodb+srv://fatigueproject:Taylorswift1988@forthsem.tdsu3zu.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where()
)

# Database
db = client["digital_fatigue_db"]

# Collection (THIS MUST MATCH YOUR ATLAS COLLECTION NAME)
metrics_collection = db["device_usage"]