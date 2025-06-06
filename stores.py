# stores.py
from flask import Blueprint, request, jsonify
from bson import ObjectId
import pymongo
from dotenv import load_dotenv
import os


# Load variables from .env into environment
load_dotenv()

# Now you can access your MONGO_URI
MONGO_URI = os.getenv("MONGO_URI")

# Initialize the Blueprint for stores
stores_bp = Blueprint('stores', __name__)

# MongoDB connection
client = pymongo.MongoClient(MONGO_URI)
db = client["store_db"]
stores_collection = db["stores"]

@stores_bp.get("/stores")
def get_stores():
    stores = []
    for store in stores_collection.find():
        store['_id'] = str(store['_id'])
        stores.append(store)
    return {'stores': stores}

@stores_bp.get("/stores/<store_id>")
def get_store(store_id):
    try:
        store = stores_collection.find_one({"_id": ObjectId(store_id)})
        if store:
            store['_id'] = str(store['_id'])
            return jsonify(store), 200
        else:
            return jsonify({"error": "Store not found"}), 404
    except:
        return jsonify({"error": "Invalid ID"}), 400

@stores_bp.post("/stores")
def create_store():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    result = stores_collection.insert_one(data)
    return jsonify({
        "message": "Store added successfully!",
        "store_id": str(result.inserted_id)
    }), 201

@stores_bp.put("/stores/<store_id>")
def update_store(store_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        result = stores_collection.update_one(
            {"_id": ObjectId(store_id)},
            {"$set": data}
        )
        if result.matched_count == 0:
            return jsonify({"error": "Store not found"}), 404
        return jsonify({"message": "Store updated successfully!"}), 200
    except:
        return jsonify({"error": "Invalid ID"}), 400

@stores_bp.delete("/stores/<store_id>")
def delete_store(store_id):
    try:
        result = stores_collection.delete_one({"_id": ObjectId(store_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Store not found"}), 404
        return jsonify({"message": "Store deleted successfully!"}), 200
    except:
        return jsonify({"error": "Invalid ID"}), 400
