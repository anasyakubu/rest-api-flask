from flask import Flask, request, jsonify
import pymongo
from bson import ObjectId  # To work with MongoDB ObjectIds

app = Flask(__name__)

# MongoDB connection
client = pymongo.MongoClient("mongodb+srv://anasyakubu:W5Q8cL3sA6VHh9rh@cluster0.9ymzbqe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["store_db"]
stores_collection = db["stores"]

# GET all stores
@app.get("/stores")
def get_stores():
    stores = []
    for store in stores_collection.find():
        store['_id'] = str(store['_id'])
        stores.append(store)
    return {'stores': stores}


# GET one store by ID
@app.get("/stores/<store_id>")
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


# CREATE a new store
@app.post("/stores")
def create_store():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    result = stores_collection.insert_one(data)
    return jsonify({
        "message": "Store added successfully!",
        "store_id": str(result.inserted_id)
    }), 201


# UPDATE a store by ID
@app.put("/stores/<store_id>")
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


# DELETE a store by ID
@app.delete("/stores/<store_id>")
def delete_store(store_id):
    try:
        result = stores_collection.delete_one({"_id": ObjectId(store_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Store not found"}), 404
        return jsonify({"message": "Store deleted successfully!"}), 200
    except:
        return jsonify({"error": "Invalid ID"}), 400


if __name__ == "__main__":
    app.run(debug=True)
