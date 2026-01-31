"""
query_engine.py - Main query engine that ties all components together
"""

from parser import Parser
from validator import Validator
from optimizer import Optimizer
from planner import Planner
from executor import Executor
from database import SCHEMA, DATABASE

class QueryEngine:
    """Main query processing engine"""
    
    def __init__(self):
        self.parser = Parser()
        self.validator = Validator(SCHEMA)
        self.optimizer = Optimizer()
        self.planner = Planner()
        self.executor = Executor(DATABASE)
    
    def execute_query(self, sql_query):
        """Execute a SQL query end-to-end"""
        try:
            print(f"\n{'='*80}")
            print(f"QUERY: {sql_query}")
            print('='*80)
            
            # 1. Parse
            print("\n1. PARSING:")
            ast = self.parser.parse(sql_query)
            print(f"   >>Abstract Syntax Tree generated")
            print(f"   {ast}")
            
        
            print("\n2. SEMANTIC VALIDATION:")
            self.validator.validate(ast)
            print("   >>Query is semantically valid")
            
           
            print("\n3. OPTIMIZATION:")
            optimized = self.optimizer.optimize(ast)
            print(f"   >>Optimizations applied: {len(optimized.get('optimizations', []))}")
            for opt in optimized.get('optimizations', []):
                print(f"     - {opt}")
            
           
            print("\n4. QUERY PLANNING:")
            plan = self.planner.create_plan(optimized)
            print(f"   >>Execution plan generated with {len(plan['steps'])} steps")
            print(f"   >>Estimated cost: {plan['cost_estimate']}")
            print(f"   >>Estimated cardinality: {plan['cardinality_estimate']}")
            
          
            print("\n5. EXECUTION:")
            results = self.executor.execute(ast)
            print(f"   >>Query executed successfully")
            print(f"   >>Results: {len(results)} row(s) returned")
            
            return results
            
        except Exception as e:
            print(f"\n>>> ERROR: {e}")
            raise