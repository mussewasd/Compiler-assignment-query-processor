Overview
QueryLang is a SQL-like query language compiler for in-memory data. It implements a complete query processing pipeline from SQL parsing to execution.

Module Architecture
1. database.py - Data Storage
python
# Stores in-memory database with schema
DATABASE = {
    "EMPLOYEES": [{"ID": 1, "NAME": "Alice", "SALARY": 50000, "DEPT_ID": 101}, ...],
    "DEPARTMENTS": [{"ID": 101, "NAME": "Engineering", "LOCATION": "NYC"}, ...]
}

SCHEMA = {
    "EMPLOYEES": {"ID": "int", "NAME": "str", "SALARY": "int", "DEPT_ID": "int"},
    "DEPARTMENTS": {"ID": "int", "NAME": "str", "LOCATION": "str"}
}
Purpose: Provides structured test data and schema for validation.

2. lexer.py - Tokenizer
python
class Lexer:
    def tokenize(self, text):
        # Converts "SELECT name FROM users" to tokens:
        # [('KEYWORD', 'SELECT'), ('ID', 'name'), ('KEYWORD', 'FROM'), ('ID', 'users')]
How it works: Uses regular expressions to break SQL into tokens (keywords, identifiers, numbers, operators).
Output: Token stream for the parser.

Example Input: SELECT name FROM employees
Token Output: [('KEYWORD', 'SELECT'), ('ID', 'name'), ('KEYWORD', 'FROM'), ('ID', 'employees')]

3. parser.py - SQL Parser Deliverable 1
python
class Parser:
    def parse(self, query):
        # Builds Abstract Syntax Tree (AST) from tokens
        # SELECT name FROM employees WHERE salary > 50000
        # → {'type': 'SELECT', 'columns': ['NAME'], 'table': 'EMPLOYEES', ...}
How it works: Recursive descent parser that consumes tokens to build AST.
Output: Abstract Syntax Tree representing query structure.

Example Input: SELECT name FROM employees WHERE salary > 50000
AST Output:

json
{
  "type": "SELECT",
  "columns": [{"type": "column", "name": "NAME"}],
  "from": {"table": {"type": "table", "name": "EMPLOYEES"}},
  "where": {
    "type": "binary_op",
    "op": ">", 
    "left": {"type": "column", "name": "SALARY"},
    "right": {"type": "literal", "value": 50000}
  }
}
4. validator.py - Semantic Checker Deliverable 2
python
class Validator:
    def validate(self, ast):
        # Checks: table exists, columns exist, types match
        # Raises: "Table 'USERS' does not exist"
How it works: Validates AST against database schema.
Output: Success or detailed error messages.

Example Validation:

text
Query: SELECT phone FROM employees
Error: Column 'PHONE' does not exist in table 'EMPLOYEES'
5. optimizer.py - Query Optimizer Deliverable 3
python
class Optimizer:
    def optimize(self, ast):
        # Applies selection pushdown:
        # SELECT * FROM (SELECT * FROM A JOIN B) WHERE A.x > 5
        # → SELECT * FROM (SELECT * FROM A WHERE x > 5 JOIN B)
How it works: Transforms AST to push WHERE conditions closer to table scans.
Output: Optimized AST with pushed-down filters.

Example Optimization:

text
Original:  SELECT * FROM employees JOIN departments WHERE salary > 50000
Optimized: Pushed condition 'salary > 50000' to table scan
6. planner.py - Query Planner Deliverable 4
python
class Planner:
    def create_plan(self, ast):
        # Creates execution plan:
        # 1. TABLE_SCAN employees
        # 2. FILTER salary > 50000  
        # 3. JOIN departments
        # 4. PROJECT name, dept_name
How it works: Converts optimized AST into step-by-step execution plan.
Output: Query execution plan with cost estimates.

Example Plan:

json
{
  "type": "QUERY_PLAN",
  "steps": [
    {"type": "TABLE_SCAN", "table": "EMPLOYEES", "cost": 100},
    {"type": "FILTER", "condition": "SALARY > 50000", "cost": 50},
    {"type": "JOIN", "tables": ["EMPLOYEES", "DEPARTMENTS"], "cost": 500},
    {"type": "PROJECT", "columns": ["NAME", "DEPT_NAME"], "cost": 10}
  ],
  "total_cost": 660
}
7. executor.py - Query Executor Deliverable 5
python
class Executor:
    def execute(self, ast):
        # Executes query plan against in-memory data
        # Returns actual query results
How it works: Interprets AST to filter, join, group, and aggregate data.
Output: Final query results.

Example Execution:

text
Input:  SELECT name, salary FROM employees WHERE salary > 50000
Output: [{'NAME': 'Bob', 'SALARY': 60000}, 
         {'NAME': 'Charlie', 'SALARY': 55000}]
8. main.py - Demonstration
python
engine = QueryEngine()
results = engine.execute_query("SELECT name FROM employees WHERE salary > 50000")
Purpose: Demonstrates complete pipeline from SQL to results.

Feature Implementation
>>SELECT-FROM-WHERE Queries
sql
SELECT name, salary FROM employees WHERE salary > 50000 AND age > 30
Implementation: Parser handles WHERE with AND/OR, executor filters rows.

>>Basic JOIN Operations
sql
SELECT e.name, d.name 
FROM employees e JOIN departments d 
ON e.dept_id = d.id
Implementation: Nested loop join in executor, handles INNER and LEFT JOIN.

>>Aggregation (COUNT, SUM, AVG)
sql
SELECT COUNT(*), AVG(salary), SUM(salary) FROM employees
Implementation: Executor aggregates data with proper grouping.

>>GROUP BY and HAVING
sql
SELECT dept_id, AVG(salary) 
FROM employees 
GROUP BY dept_id 
HAVING AVG(salary) > 50000
Implementation: Two-phase aggregation with group filtering.

??Nested Queries (Limited)
sql
SELECT name FROM employees 
WHERE salary > (SELECT AVG(salary) FROM employees)
Implementation: Parser supports syntax, basic execution.

Complete Pipeline Example
Input Query:

sql
SELECT name, salary FROM employees WHERE salary > 50000
Pipeline Flow:

Lexer: [SELECT, name, FROM, employees, WHERE, salary, >, 50000]

Parser: AST with SELECT, columns, table, WHERE condition

Validator: Checks employees table exists, name/salary columns exist

Optimizer: Pushes salary > 50000 to table scan

Planner: Creates plan: SCAN → FILTER → PROJECT

Executor: Filters employees, selects name/salary columns

Output: [{'NAME': 'Bob', 'SALARY': 60000}, ...]

Sample Output
text


SELECT-FROM-WHERE

Query: SELECT NAME, SALARY FROM EMPLOYEES WHERE SALARY > 50000
Result (3 rows):
  {'NAME': 'Bob', 'SALARY': 60000}
  {'NAME': 'Charlie', 'SALARY': 55000}
  {'NAME': 'Diana', 'SALARY': 70000}

JOIN Operation

Query: SELECT E.NAME, D.NAME FROM EMPLOYEES E JOIN DEPARTMENTS D ON E.DEPT_ID = D.ID
Result (6 rows):
  {'NAME': 'Alice', 'NAME': 'Engineering'}
  {'NAME': 'Bob', 'NAME': 'Sales'}
  {'NAME': 'Charlie', 'NAME': 'Engineering'}
  {'NAME': 'Diana', 'NAME': 'Marketing'}
  {'NAME': 'Eve', 'NAME': 'Sales'}
  {'NAME': 'Frank', 'NAME': 'Engineering'}

GROUP BY with HAVING

Query: SELECT DEPT_ID, AVG(SALARY) FROM EMPLOYEES GROUP BY DEPT_ID HAVING AVG(SALARY) > 50000
Result (2 rows):
  {'DEPT_ID': 101, 'AVG': 51000.0}
  {'DEPT_ID': 103, 'AVG': 70000.0}

