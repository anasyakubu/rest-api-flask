# stores.py
from flask import Blueprint, request, jsonify
from bson import ObjectId
import pymongo
from dotenv import load_dotenv
import os
from services.vat import calculated_vat
import jwt
from functools import wraps

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET = os.getenv("JWT_SECRET", "secret")

# Initialize Blueprint
stores_bp = Blueprint('stores', __name__)

# MongoDB connection
client = pymongo.MongoClient(MONGO_URI)
db = client["store_db"]
stores_collection = db["stores"]
users_collection = db["users"]

# JWT Decorator (same as in users.py)
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({"error": "Token is missing!"}), 401
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            current_user = users_collection.find_one({"_id": ObjectId(data["user_id"])})
            if not current_user:
                return jsonify({"error": "Invalid token!"}), 401
            current_user["_id"] = str(current_user["_id"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired!"}), 401
        except Exception:
            return jsonify({"error": "Invalid token!"}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@stores_bp.get("/stores")
@token_required
def get_stores(current_user):
    stores = []
    for store in stores_collection.find():
        store['_id'] = str(store['_id'])
        stores.append(store)
    return jsonify({"stores": stores}), 200

@stores_bp.get("/stores/<store_id>")
@token_required
def get_store(current_user, store_id):
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
@token_required
def create_store(current_user):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "name" not in data or "items" not in data:
        return jsonify({"error": "Missing required fields (name, items)"}), 400

    for item in data["items"]:
        price = item.get("price", 0)
        item["vat"] = calculated_vat(price)

    result = stores_collection.insert_one(data)

    return jsonify({
        "message": "Store added successfully!",
        "store_id": str(result.inserted_id)
    }), 201

@stores_bp.put("/stores/<store_id>")
@token_required
def update_store(current_user, store_id):
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
@token_required
def delete_store(current_user, store_id):
    try:
        result = stores_collection.delete_one({"_id": ObjectId(store_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Store not found"}), 404
        return jsonify({"message": "Store deleted successfully!"}), 200
    except:
        return jsonify({"error": "Invalid ID"}), 400
