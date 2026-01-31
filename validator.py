"""
validator.py - Fixed semantic analyzer and validator
"""

from database import SCHEMA

class Validator:
    """Validates SQL queries against schema and semantic rules"""
    
    def __init__(self, schema):
        self.schema = schema
        self.current_tables = {}
        self.errors = []
    
    def validate(self, query_ast):
        """Validate a query AST"""
        self.errors = []
        self.current_tables = {}
        
     
        self.validate_from_clause(query_ast['from'])
        
 
        self.validate_columns(query_ast['columns'])
        
       
        if query_ast['where']:
            self.validate_expression(query_ast['where'])
        

        if query_ast['group_by']:
            self.validate_group_by(query_ast['group_by'], query_ast['columns'])
        
     
        if query_ast['having']:
            self.validate_expression(query_ast['having'])
        
   
        if query_ast['order_by']:
            self.validate_order_by(query_ast['order_by'])
        
        if self.errors:
            raise ValueError("; ".join(self.errors))
        
        return True
    
    def validate_from_clause(self, from_clause):
        """Validate FROM clause and collect table information"""
        main_table = from_clause['table']
        self.validate_table_reference(main_table)
        
        for join in from_clause['joins']:
            self.validate_table_reference(join['table'])
            self.validate_expression(join['condition'])
    
    def validate_table_reference(self, table_ref):
        """Validate table reference"""
        table_name = table_ref['name']
        alias = table_ref.get('alias', table_name)
        
        if table_name not in self.schema:
            self.errors.append(f"Table '{table_name}' does not exist")
            return

        self.current_tables[alias] = {
            'name': table_name,
            'schema': self.schema[table_name]
        }
    
    def validate_columns(self, columns):
        """Validate SELECT columns"""
        for col in columns:
            self.validate_column_expression(col)
    
    def validate_column_expression(self, col_expr):
        """Validate a column expression"""
        if col_expr['type'] == 'all':
            return  
        
        elif col_expr['type'] == 'function':
         
            if isinstance(col_expr['args'], dict):
                self.validate_expression(col_expr['args'])
        
        elif col_expr['type'] == 'column':
            self.validate_column_reference(col_expr)
        
        elif col_expr['type'] == 'binary_op':
            self.validate_expression(col_expr)
    
    def validate_column_reference(self, column_ref):
        """Validate column reference against tables"""
        column_name = column_ref.get('name')
        table_name = column_ref.get('table')
        
        if table_name:
  
            if table_name not in self.current_tables:
                self.errors.append(f"Table alias '{table_name}' not in FROM clause")
                return
            
            table_info = self.current_tables[table_name]
            if column_name not in table_info['schema']:
                self.errors.append(f"Column '{table_name}.{column_name}' does not exist in table '{table_info['name']}'")
        else:
         
            found_tables = []
            for alias, table_info in self.current_tables.items():
                if column_name in table_info['schema']:
                    found_tables.append(alias)
            
            if len(found_tables) == 0:
                self.errors.append(f"Column '{column_name}' does not exist in any table")
            elif len(found_tables) > 1:
                self.errors.append(f"Column '{column_name}' is ambiguous (exists in tables: {', '.join(found_tables)})")
    
    def validate_expression(self, expr):
        """Validate any expression"""
        if expr['type'] == 'binary_op':
            self.validate_expression(expr['left'])
            self.validate_expression(expr['right'])
        
        elif expr['type'] == 'column':
            self.validate_column_reference(expr)
        
        elif expr['type'] == 'function':
            if isinstance(expr['args'], dict):
                self.validate_expression(expr['args'])
    
    def validate_group_by(self, group_by, select_columns):
        """Validate GROUP BY clause"""

        for col_expr in group_by:
            self.validate_column_expression(col_expr)
    
    def validate_order_by(self, order_by):
        """Validate ORDER BY clause"""
        for item in order_by:
            self.validate_expression(item['expr'])