# config.py
import os

# Environment variables
BOT_TOKEN = "7805936590:AAGAea8dSNxdR2YOUTw8FmthCIuRVLYK3Y8"
AUTHORIZED_MANAGER_IDS = [6463294729, 30209376]

# Employee Details with IDs, Names, and Family
EMPLOYEES = {
    61002957: {"role": "Operations", "name": "Operations Employee 1", "family": "Family 1"},
    6463294729: {"role": "Operations", "name": "Farhan", "family": "Kardan"},
    61002975: {"role": "Sales", "name": "Sales Employee 1", "family": "Family 2"},
    1234567890: {"role": "Sales", "name": "Employee Name Sales", "family": "Family Sales"},
}

# Derived Groups
OPERATIONS_EMPLOYEES = [emp_id for emp_id, details in EMPLOYEES.items() if details["role"] == "Operations"]
SALES_EMPLOYEES = [emp_id for emp_id, details in EMPLOYEES.items() if details["role"] == "Sales"]

# Authorized Users
AUTHORIZED_USER_IDS = list(EMPLOYEES.keys())


