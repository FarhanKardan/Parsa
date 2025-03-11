import logging
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from config import EMPLOYEES

# Configure logger
logger = logging.getLogger(__name__)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")  # Use your MongoDB connection string
db = client["employee_management"]
boxes_db = client['box_database']
boxes_collection = boxes_db['boxes']

# ----------------- Box Manager Functions -----------------

# Helper function to insert a box into the database with formatted timestamp
def insert_box(box_id: str, shop_category: str) -> bool:
    try:
        box = {
            "box_id": box_id,
            "shop_category": shop_category,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Format the timestamp
        }
        boxes_collection.insert_one(box)
        return True
    except Exception as e:
        logger.error(f"Error inserting box: {e}")
        return False

# Helper function to update a box category
def update_box_category(box_id: str, new_shop_category: str) -> bool:
    try:
        result = boxes_collection.update_one(
            {"box_id": box_id},
            {"$set": {"shop_category": new_shop_category, "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}
        )
        return result.modified_count > 0  # Return True if the update was successful
    except Exception as e:
        logger.error(f"Error updating box category: {e}")
        return False

# Helper function to get box details by box_id
def get_box_details(box_id: str):
    try:
        box = boxes_collection.find_one({"box_id": box_id})
        if box:
            return f"Box ID: {box['box_id']}\nShop Category: {box['shop_category']}\nTimestamp: {box['timestamp']}"
        else:
            return "Box not found."
    except Exception as e:
        logger.error(f"Error retrieving box details: {e}")
        return "Error retrieving box details."

# Helper function to remove a box by box_id
def remove_box(box_id: str) -> bool:
    try:
        result = boxes_collection.delete_one({"box_id": box_id})
        return result.deleted_count > 0  # Return True if a box was successfully removed
    except Exception as e:
        logger.error(f"Error removing box: {e}")
        return False

