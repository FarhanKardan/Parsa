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

# ----------------- Employee Leave Management Functions -----------------

# Function to add a leave request
def add_leave_request(employee_id, date, reason):
    try:
        # Fetch employee details
        employee_details = EMPLOYEES.get(employee_id, {"name": "Unknown", "family": "Unknown", "role": "Unknown"})
        name = employee_details["name"]
        family = employee_details["family"]
        role = employee_details["role"]

        # Create the leave request dictionary
        request = {
            "employee_id": employee_id,
            "name": name,
            "family": family,
            "role": role,
            "date": date,
            "reason": reason,
            "status": "pending"
        }

        # Insert the leave request into the database
        result = db.requests.insert_one(request)
        logger.info(f"Leave request added: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        logger.error(f"Error adding leave request: {e}")
        return None

# Function to fetch all pending leave requests
def get_pending_requests():
    try:
        return list(db.requests.find({"status": "pending"}))
    except Exception as e:
        logger.error(f"Error fetching pending requests: {e}")
        return []

# Function to update the status of a leave request
def update_request_status(request_id, status):
    try:
        return db.requests.find_one_and_update(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": status}},
            return_document=True
        )
    except Exception as e:
        logger.error(f"Error updating request status: {e}")
        return None

# Function to get approved leave requests by employee class
def get_approved_requests_by_class(employee_class):
    try:
        approved_requests = db.requests.find({
            "status": "approved", 
            "employee_class": employee_class
        })
        return list(approved_requests)
    except Exception as e:
        logger.error(f"Error fetching approved requests for class {employee_class}: {e}")
        return []

# Function to check if an employee has any pending or approved leave requests
def has_pending_or_approved_requests(employee_id):
    try:
        result = db['requests'].count_documents({
            "employee_id": employee_id,
            "$or": [{"status": "pending"}, {"status": "approved"}]
        })
        return result > 0
    except Exception as e:
        logger.error(f"Error checking pending or approved requests: {e}")
        return False
    
# Function to get the number of leave requests for an employee
def get_leave_request_count(employee_id):
    try:
        count = db.requests.count_documents({"employee_id": employee_id})
        return count
    except Exception as e:
        logger.error(f"Error fetching leave request count for employee {employee_id}: {e}")
        return 0
