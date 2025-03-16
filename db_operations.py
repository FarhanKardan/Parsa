import logging
from pymongo import MongoClient
from bson import ObjectId
from config import EMPLOYEES
from datetime import datetime, timedelta
import jdatetime
from collections import defaultdict

# Configure logger
logger = logging.getLogger(__name__)

client =MongoClient("mongodb://localhost:27017/")
db = client["ParsaKala"]
boxes_db = client['ParsaKala']
boxes_collection = boxes_db['boxes']

# ----------------- Employee Leave Management Functions -----------------

# Helper function to get employee details
def get_employee_details(employee_id):
    return EMPLOYEES.get(employee_id, {"name": "Unknown", "family": "Unknown", "role": "Unknown"})

# Function to add a leave request
def add_leave_request(employee_id, date, reason):
    try:
        # Fetch employee details
        employee_details = get_employee_details(employee_id)
        request = {
            "employee_id": employee_id,
            "name": employee_details["name"],
            "family": employee_details["family"],
            "role": employee_details["role"],
            "date": date,
            "reason": reason,
            "status": "pending"
        }

        # Insert the leave request into the database
        result = db.requests.insert_one(request)
        logger.info(f"Leave request added for {employee_details['name']} {employee_details['family']} with ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        logger.error(f"Error adding leave request for employee {employee_id}: {e}")
        return None

# Function to fetch all pending leave requests
def get_pending_requests():
    try:
        pending_requests = list(db.requests.find({"status": "pending"}))
        logger.info(f"Fetched {len(pending_requests)} pending requests.")
        return pending_requests
    except Exception as e:
        logger.error(f"Error fetching pending requests: {e}")
        return []

# Function to update the status of a leave request
def update_request_status(request_id, status):
    try:
        updated_request = db.requests.find_one_and_update(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": status}},
            return_document=True
        )
        if updated_request:
            logger.info(f"Leave request {request_id} status updated to {status}.")
        else:
            logger.warning(f"Request {request_id} not found for status update.")
        return updated_request
    except Exception as e:
        logger.error(f"Error updating request status for request {request_id}: {e}")
        return None

# Function to check if an employee has any pending or approved leave requests
def has_pending_or_approved_requests(employee_id):
    try:
        # Use $or to check both pending and approved statuses in a single query
        pending_or_approved = db.requests.count_documents({
            "employee_id": employee_id,
            "$or": [{"status": "pending"}, {"status": "approved"}]
        })
        has_requests = pending_or_approved > 0
        logger.info(f"Employee {employee_id} has {'pending or approved' if has_requests else 'no'} leave requests.")
        return has_requests
    except Exception as e:
        logger.error(f"Error checking pending or approved requests for employee {employee_id}: {e}")
        return False

# Function to get the number of leave requests for an employee
def get_leave_request_count(employee_id):
    try:
        # Count all leave requests for the employee
        count = db.requests.count_documents({"employee_id": employee_id})
        logger.info(f"Employee {employee_id} has {count} leave requests.")
        return count
    except Exception as e:
        logger.error(f"Error fetching leave request count for employee {employee_id}: {e}")
        return 0

# Function to fetch approved leave requests by employee class (if needed)
def get_approved_requests_by_class(employee_class):
    try:
        approved_requests = list(db.requests.find({
            "status": "approved", 
            "employee_class": employee_class
        }))
        logger.info(f"Fetched {len(approved_requests)} approved requests for class {employee_class}.")
        return approved_requests
    except Exception as e:
        logger.error(f"Error fetching approved requests for class {employee_class}: {e}")
        return []
    
# Function to convert a Gregorian date to Jalali date
def convert_to_jalali(date):
    return jdatetime.datetime.fromgregorian(datetime=date).strftime("%Y-%m")


# ----------------- Box Manager Functions -----------------

# Helper function to insert a box into the database with formatted timestamp
def insert_box(box_id: str, shop_category: str, icloud_id: str, imei_1: str, imei_2: str, name_family: str) -> bool:
    try:
        box = {
            "box_id": box_id,
            "shop_category": shop_category,
            "icloud_id": icloud_id,
            "imei_1": imei_1,
            "imei_2": imei_2,
            "name_family": name_family,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Format the timestamp
        }
        boxes_collection.insert_one(box)
        logger.info(f"Box {box_id} inserted successfully.")
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
        box = boxes_collection.find_one({"imei_1": box_id})
        if box:
            details = (
                "جزئیات جعبه:\n\n"
                f"شناسه جعبه: {box['box_id']}\n"
                f"دسته‌بندی فروشگاه: {box['shop_category']}\n"
                f"آیدی ایکلود: {box.get('icloud_id', 'N/A')}\n"
                f"چهار رقم آخر سریال دستگاه (IMEI 1): {box.get('imei_1', 'N/A')}\n"
                f"چهار رقم آخر سریال دستگاه (IMEI 2): {box.get('imei_2', 'N/A')}\n"
                f"نام و نام خانوادگی: {box.get('name_family', 'N/A')}\n"
                f"زمان ثبت: {box['timestamp']}"
            )
            return details
        else:
            return "جعبه با این IMEI 1 یافت نشد."
    except Exception as e:
        logger.error(f"Error retrieving box details: {e}")
        return "خطا در دریافت جزئیات جعبه. لطفاً دوباره تلاش کنید."

# Helper function to remove a box by box_id
def remove_box(box_id: str) -> bool:
    try:
        result = boxes_collection.delete_one({"box_id": box_id})
        return result.deleted_count > 0  # Return True if a box was successfully removed
    except Exception as e:
        logger.error(f"Error removing box: {e}")
        return False