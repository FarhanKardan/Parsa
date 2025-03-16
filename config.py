import os

# Environment variables
BOT_TOKEN = "7775555458:AAHSOUrl3Vt9AlAScrkwvXo_jLqC3sANixw"

AUTHORIZED_MANAGER_IDS = [61002957,115864862]

# Employee Details with IDs, Names, and Family
EMPLOYEES = {
    6463294729: {"role": "Operations", "name": "Farhan", "family": "Kardan"},
    134124009: {"role": "Operations", "name": "Masiha", "family": "Armin"},
    66185098: {"role": "Operations", "name": "Homa", "family": "Fadayi"},
    210610395: {"role": "Operations", "name": "Arash", "family": "Nazeri"},
    79266209: {"role": "Operations", "name": "Mohammad", "family": "Kiani"},
    103244004: {"role": "Operations", "name": "Zahra", "family": "Karami"},
    79307601: {"role": "Sales", "name": "Babak", "family": "Eftekhar"},
    11984453885: {"role": "Sales", "name": "Ashkan", "family": "Porshir"},
    103900682: {"role": "Sales", "name": "Masoud", "family": "Armin"},
    318270721: {"role": "Sales", "name": "Alireza", "family": "Arab"},
    618685441: {"role": "Operations", "name": "Nazanin", "family": "Mirzayi"},
    5808136777: {"role": "Sales", "name": "Naser", "family": "Kiani"},
    6118872231: {"role": "Sales", "name": "Alireza", "family": "Bakherzi"},

}

# Derived Groups
OPERATIONS_EMPLOYEES = [emp_id for emp_id, details in EMPLOYEES.items() if details["role"] == "Operations"]
SALES_EMPLOYEES = [emp_id for emp_id, details in EMPLOYEES.items() if details["role"] == "Sales"]



# Authorized Users
AUTHORIZED_USER_IDS = list(EMPLOYEES.keys()) + AUTHORIZED_MANAGER_IDS





