from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

# Blueprints
from routes.predict import predict_bp
from routes.analyze import analyze_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(predict_bp)
app.register_blueprint(analyze_bp)

# MongoDB connection
MONGO_URI = "mongodb+srv://fatigueproject:Taylorswift1988@forthsem.tdsu3zu.mongodb.net/digital_fatigue_db?retryWrites=true&w=majority&appName=forthsem"

client = MongoClient(MONGO_URI)
db = client["digital_fatigue_db"]
collection = db["device_usage"]

@app.route("/")
def home():
    return jsonify({
        "message": "AI-Based Digital Fatigue Backend is running"
    })

@app.route("/collect-data", methods=["POST"])
def collect_data():
    data = request.json
    data["timestamp"] = datetime.utcnow()
    collection.insert_one(data)

    return jsonify({
        "status": "success",
        "message": "Data stored successfully"
    })

@app.route("/health")
def health():
    return jsonify({"status": "OK"})

if __name__ == "__main__":
    app.run(debug=True)
