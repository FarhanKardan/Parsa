import logging
import datetime
# Configure logger
logger = logging.getLogger(__name__)
from config import EMPLOYEES, OPERATIONS_EMPLOYEES, SALES_EMPLOYEES



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
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        logger.error(f"Invalid date format: {date_str}")
        return False


