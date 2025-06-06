from flask import Flask
import pymongo

app = Flask(__name__)

# MongoDB connection
client = pymongo.MongoClient("mongodb+srv://anasyakubu:W5Q8cL3sA6VHh9rh@cluster0.9ymzbqe.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Database and collection
db = client["store_db"]
stores_collection = db["stores"]

# Create a list to store all documents
stores = []
for x in stores_collection.find():
    stores.append(x)

@app.get("/stores")  # http://127.0.0.1:5000/stores
def get_stores():
    # Convert ObjectId to string for JSON serialization (optional)
    for store in stores:
        if '_id' in store:
            store['_id'] = str(store['_id'])
    return {'stores': stores}
