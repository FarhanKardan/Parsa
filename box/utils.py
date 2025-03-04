import logging
import config  # Import config file for the configuration
import datetime

# Configure logger
logger = logging.getLogger(__name__)
from config import EMPLOYEES, OPERATIONS_EMPLOYEES, SALES_EMPLOYEES, AUTHORIZED_USER_IDS

# Function to get employee details by ID
def get_employee_details(employee_id):
    return EMPLOYEES.get(employee_id, {"name": "Unknown", "family": "Unknown", "role": "Unknown"})

# Function to check if the employee is in the Operations group
def is_operations_employee(employee_id):
    return employee_id in OPERATIONS_EMPLOYEES

# Function to check if the employee is in the Sales group
def is_sales_employee(employee_id):
    return employee_id in SALES_EMPLOYEES

# Function to validate date format
def validate_date(date_str):
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        logger.error(f"Invalid date format: {date_str}")
        return False

# Function to check if the user is a manager
def is_manager(user_id):
    if user_id in config.AUTHORIZED_MANAGER_IDS:
        return True
    logger.warning(f"Unauthorized manager access attempt by user {user_id}")
    return False

# Function to check if the user is an employee
def is_employee(user_id):
    if user_id in AUTHORIZED_USER_IDS:
        return True
    logger.warning(f"Unauthorized employee access attempt by user {user_id}")
    return False

# Example Usage
user_id = 61002957
if is_employee(user_id):
    details = get_employee_details(user_id)
    print(f"Employee Name: {details['name']} {details['family']}, Role: {details['role']}")
