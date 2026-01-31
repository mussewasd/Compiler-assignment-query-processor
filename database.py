"""
database.py - Database schema and sample data
"""


SCHEMA = {
    "EMPLOYEES": {
        "ID": {"type": "int", "nullable": False},
        "NAME": {"type": "str", "nullable": False},
        "DEPT_ID": {"type": "int", "nullable": False},
        "SALARY": {"type": "int", "nullable": False},
        "AGE": {"type": "int", "nullable": False},
        "HIRE_DATE": {"type": "date", "nullable": False}
    },
    "DEPARTMENTS": {
        "ID": {"type": "int", "nullable": False},
        "NAME": {"type": "str", "nullable": False},
        "LOCATION": {"type": "str", "nullable": False},
        "BUDGET": {"type": "int", "nullable": False}
    },
    "SALES": {
        "ID": {"type": "int", "nullable": False},
        "EMPLOYEE_ID": {"type": "int", "nullable": False},
        "PRODUCT": {"type": "str", "nullable": False},
        "AMOUNT": {"type": "int", "nullable": False},
        "QUARTER": {"type": "str", "nullable": False},
        "YEAR": {"type": "int", "nullable": False}
    }
}


DATABASE = {
    "EMPLOYEES": [
        {"ID": 1, "NAME": "Alice", "DEPT_ID": 101, "SALARY": 50000, "AGE": 30, "HIRE_DATE": "2020-01-15"},
        {"ID": 2, "NAME": "Bob", "DEPT_ID": 102, "SALARY": 60000, "AGE": 25, "HIRE_DATE": "2019-03-20"},
        {"ID": 3, "NAME": "Charlie", "DEPT_ID": 101, "SALARY": 55000, "AGE": 35, "HIRE_DATE": "2018-07-10"},
        {"ID": 4, "NAME": "Diana", "DEPT_ID": 103, "SALARY": 70000, "AGE": 28, "HIRE_DATE": "2021-02-28"},
        {"ID": 5, "NAME": "Eve", "DEPT_ID": 102, "SALARY": 45000, "AGE": 32, "HIRE_DATE": "2020-11-05"},
        {"ID": 6, "NAME": "Frank", "DEPT_ID": 101, "SALARY": 48000, "AGE": 29, "HIRE_DATE": "2019-09-15"}
    ],
    "DEPARTMENTS": [
        {"ID": 101, "NAME": "Engineering", "LOCATION": "NYC", "BUDGET": 1000000},
        {"ID": 102, "NAME": "Sales", "LOCATION": "LA", "BUDGET": 800000},
        {"ID": 103, "NAME": "Marketing", "LOCATION": "Chicago", "BUDGET": 600000},
        {"ID": 104, "NAME": "HR", "LOCATION": "Boston", "BUDGET": 400000}
    ],
    "SALES": [
        {"ID": 1, "EMPLOYEE_ID": 1, "PRODUCT": "Laptop", "AMOUNT": 1000, "QUARTER": "Q1", "YEAR": 2023},
        {"ID": 2, "EMPLOYEE_ID": 1, "PRODUCT": "Tablet", "AMOUNT": 500, "QUARTER": "Q1", "YEAR": 2023},
        {"ID": 3, "EMPLOYEE_ID": 2, "PRODUCT": "Phone", "AMOUNT": 800, "QUARTER": "Q1", "YEAR": 2023},
        {"ID": 4, "EMPLOYEE_ID": 2, "PRODUCT": "Laptop", "AMOUNT": 1200, "QUARTER": "Q2", "YEAR": 2023},
        {"ID": 5, "EMPLOYEE_ID": 3, "PRODUCT": "Tablet", "AMOUNT": 600, "QUARTER": "Q2", "YEAR": 2023},
        {"ID": 6, "EMPLOYEE_ID": 4, "PRODUCT": "Phone", "AMOUNT": 900, "QUARTER": "Q3", "YEAR": 2023},
        {"ID": 7, "EMPLOYEE_ID": 5, "PRODUCT": "Laptop", "AMOUNT": 1100, "QUARTER": "Q3", "YEAR": 2023},
        {"ID": 8, "EMPLOYEE_ID": 1, "PRODUCT": "Phone", "AMOUNT": 700, "QUARTER": "Q4", "YEAR": 2023}
    ]
}