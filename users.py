# users.py
from flask import Blueprint, request, jsonify
import pymongo
from bson import ObjectId
from dotenv import load_dotenv
import os
import jwt
import datetime
from functools import wraps

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
JWT_SECRET = os.getenv("JWT_SECRET", "secret")  # Use .env for security

# Initialize Blueprint
users_bp = Blueprint('users', __name__)

# MongoDB connection
client = pymongo.MongoClient(MONGO_URI)
db = client["store_db"]
users_collection = db["users"]

# Utility: JWT Decorator
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

@users_bp.post("/users")
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    if "name" not in data or "email" not in data or "password" not in data:
        return jsonify({"error": "Missing required fields (name, email, password)"}), 400

    # Check if user exists
    if users_collection.find_one({"email": data["email"]}):
        return jsonify({"error": "Email already exists"}), 400

    result = users_collection.insert_one(data)
    return jsonify({
        "message": "User created successfully!",
        "user_id": str(result.inserted_id)
    }), 201

@users_bp.post("/login")
def login():
    data = request.get_json()
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Missing email or password"}), 400

    user = users_collection.find_one({"email": data["email"], "password": data["password"]})
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({
        "user_id": str(user["_id"]),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, JWT_SECRET, algorithm="HS256")

    return jsonify({"token": token}), 200
    

@users_bp.get("/users")
@token_required
def get_users(current_user):
    users = []
    for user in users_collection.find():
        user["_id"] = str(user["_id"])
        users.append(user)
    return jsonify({"users": users}), 200




@users_bp.get("/users/<user_id>")
@token_required
def get_user(current_user, user_id):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
            return jsonify(user), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except:
        return jsonify({"error": "Invalid ID"}), 400
    


@users_bp.put("/users/<user_id>")
@token_required
def update_user(current_user, user_id):
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
@token_required
def delete_user(current_user, user_id):
    try:
        result = users_collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "User not found"}), 404
        return jsonify({"message": "User deleted successfully!"}), 200
    except:
        return jsonify({"error": "Invalid ID"}), 400
