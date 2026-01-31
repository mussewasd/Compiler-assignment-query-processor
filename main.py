

from parser import Parser
from validator import Validator
from optimizer import Optimizer
from planner import Planner
from executor import Executor
from database import SCHEMA, DATABASE

class QueryEngine:
    def __init__(self):
        self.parser = Parser()
        self.validator = Validator(SCHEMA)
        self.optimizer = Optimizer()
        self.planner = Planner()
        self.executor = Executor(DATABASE)
    
    def execute_query(self, sql_query):
        try:
            # 1. Parse
            ast = self.parser.parse(sql_query)
            
            # 2. Validate
            self.validator.validate(ast)
            
            # 3. Optimize
            optimized = self.optimizer.optimize(ast)
            
            # 4. Plan
            plan = self.planner.create_plan(optimized)
            
            # 5. Execute
            results = self.executor.execute(ast)
            
            return {
                'ast': ast,
                'plan': plan,
                'results': results
            }
            
        except Exception as e:
            print(f"Error: {e}")
            return None

def main():
    engine = QueryEngine()
    
   
    
    test_cases = [
        ("SELECT-FROM-WHERE", "SELECT NAME, SALARY FROM EMPLOYEES WHERE SALARY > 50000"),
        ("JOIN Operation", "SELECT E.NAME, D.NAME FROM EMPLOYEES E JOIN DEPARTMENTS D ON E.DEPT_ID = D.ID"),
        ("COUNT Aggregation", "SELECT COUNT(*) FROM EMPLOYEES"),
        ("SUM Aggregation", "SELECT SUM(SALARY) FROM EMPLOYEES"),
        ("AVG Aggregation", "SELECT AVG(SALARY) FROM EMPLOYEES"),
        ("GROUP BY", "SELECT DEPT_ID, COUNT(*) FROM EMPLOYEES GROUP BY DEPT_ID"),
        ("GROUP BY with HAVING", "SELECT DEPT_ID, AVG(SALARY) FROM EMPLOYEES GROUP BY DEPT_ID HAVING AVG(SALARY) > 50000"),
    ]
    
    for test_name, query in test_cases:
        print(f"\n{test_name}")
        print("-" * 40)
        print(f"Query: {query}")
        
        result = engine.execute_query(query)
        if result:
            results = result['results']
            if results:
                print(f"Result ({len(results)} rows):")
                for row in results:
                    print(f"  {row}")
            else:
                print("Result: []")
        else:
            print("Result: Failed to execute")
    
  

if __name__ == "__main__":
    main()