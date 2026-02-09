from flask import Blueprint, request, jsonify

collect_bp = Blueprint("collect", __name__)

@collect_bp.route("/collect-data", methods=["POST"])
def collect_data():
    data = request.json

    if not data:
        return jsonify({"error": "No data received"}), 400

    return jsonify({
        "message": "Data received successfully",
        "received_data": data
    }), 200
