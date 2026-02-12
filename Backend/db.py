from pymongo import MongoClient
import certifi

MONGO_URI = "mongodb+srv://fatigueproject:Taylorswift1988@forthsem.tdsu3zu.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=5000
)

db = client["digital_fatigue_db"]
collection = db["device_usage"]
