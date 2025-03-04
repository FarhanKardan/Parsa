import logging
from pymongo import MongoClient
from bson import ObjectId
from config import EMPLOYEES

# Configure logger
logger = logging.getLogger(__name__)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["employee_management"]

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

def get_pending_requests():
    try:
        return list(db.requests.find({"status": "pending"}))
    except Exception as e:
        logger.error(f"Error fetching pending requests: {e}")
        return []

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

def has_pending_or_approved_requests(employee_id):
    try:
        result = db['requests'].count_documents({
            "employee_id": employee_id,
            "$or": [{"status": "pending"}]
        })
        return result > 0
    except Exception as e:
        logger.error(f"Error checking pending or approved requests: {e}")
        return False
