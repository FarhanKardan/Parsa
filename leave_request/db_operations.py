import logging
from pymongo import MongoClient
from bson import ObjectId
from config import EMPLOYEES
from datetime import datetime, timedelta
import jdatetime
from collections import defaultdict

# Configure logger
logger = logging.getLogger(__name__)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")  # Use your MongoDB connection string
db = client["ParsaKala"]

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


# Function to fetch and summarize approved leave requests by Jalali month
def get_approved_leave_requests_by_jalali_month():
    try:
        # Calculate the date 60 days ago
        sixty_days_ago = datetime.now() - timedelta(days=60)

        # Aggregation pipeline to fetch approved leave requests within the last 60 days
        pipeline = [
            {
                "$match": {
                    "status": "approved",  # Only consider approved leave requests
                    "date": {"$gte": sixty_days_ago}  # Filter for requests within the last 60 days
                }
            },
            {
                "$lookup": {
                    "from": "employees",  # Assuming there is an 'employees' collection
                    "localField": "employee_id",
                    "foreignField": "employee_id",
                    "as": "employee_details"
                }
            },
            {
                "$unwind": "$employee_details"  # Unwind the 'employee_details' array to get individual fields
            }
        ]

        # Execute the query to fetch the data
        leave_requests = list(db.requests.aggregate(pipeline))

        # Group the leave requests based on Jalali months and sum them
        leave_by_jalali_month = defaultdict(lambda: defaultdict(int))

        # Loop through the leave requests and process them
        for request in leave_requests:
            # Convert the leave request date to Jalali month
            jalali_month = convert_to_jalali(request['date'])
            
            # Group by Jalali month and employee_id
            employee_name = request['employee_details']['name']
            employee_family = request['employee_details']['family']
            employee_id = request['employee_id']
            
            leave_by_jalali_month[jalali_month][employee_id] += 1  # Count the leave requests

        # Return the summarized leave data
        return leave_by_jalali_month

    except Exception as e:
        print(f"Error fetching or processing leave requests: {e}")
        return {}
    