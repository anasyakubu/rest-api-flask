# users.py
from flask import Blueprint, request, jsonify
import pymongo
from bson import ObjectId
from dotenv import load_dotenv
import os


# Load variables from .env into environment
load_dotenv()

# Now you can access your MONGO_URI
MONGO_URI = os.getenv("MONGO_URI")

# Initialize the Blueprint for users
users_bp = Blueprint('users', __name__)

# MongoDB connection
client = pymongo.MongoClient(MONGO_URI)
db = client["store_db"]
users_collection = db["users"]



@users_bp.post("/users")
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "name" not in data or "email" not in data or "password" not in data:
        return jsonify({"error": "Missing required fields (name, email, password)"}), 400

    result = users_collection.insert_one(data)
    return jsonify({
        "message": "User created successfully!",
        "user_id": str(result.inserted_id)
    }), 201




@users_bp.get("/users")
def get_users():
    users = []
    for user in users_collection.find():
        user['_id'] = str(user['_id'])
        users.append(user)
    return jsonify({"users": users}), 200



@users_bp.get("/users/<user_id>")
def get_user(user_id):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user['_id'] = str(user['_id'])
            return jsonify(user), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except:
        return jsonify({"error": "Invalid ID"}), 400
    



@users_bp.put("/users/<user_id>")
def update_user(user_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        result = users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": data}
        )
        if result.matched_count == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User updated successfully!"}), 200
    except:
        return jsonify({"error": "Invalid ID"}), 400
    


@users_bp.delete("/users/<user_id>")
def delete_user(user_id):
    try:
        result = users_collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User deleted successfully!"}), 200
    except:
        return jsonify({"error": "Invalid ID"}), 400
