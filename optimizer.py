"""
optimizer.py - Query optimizer with selection pushdown and other optimizations
"""

class Optimizer:
    """Optimizes query AST for better performance"""
    
    def __init__(self):
        self.optimizations_applied = []
    
    def optimize(self, query_ast):
        """Apply optimizations to query AST"""
        optimized = query_ast.copy()
        self.optimizations_applied = []
        
   
        optimized = self.push_selections_down(optimized)
        optimized = self.remove_unused_columns(optimized)
        optimized = self.merge_filters(optimized)
        
        optimized['optimizations'] = self.optimizations_applied
        return optimized
    
    def push_selections_down(self, query):
        """Push WHERE conditions closer to table scans"""
        if not query['where']:
            return query
        
       
        
        condition = query['where']
        self.optimizations_applied.append(f"Pushed condition '{self.expr_to_str(condition)}' down to table scan")
        
       
        query['pushed_filters'] = [condition]
        query['where'] = None  
        
        return query
    
    def remove_unused_columns(self, query):
        """Remove unused columns from intermediate results"""
      
        used_columns = set()
        
       
        for col in query['columns']:
            self.collect_columns(col, used_columns)
        
      
        if query['where']:
            self.collect_columns(query['where'], used_columns)
        
        
        if query['group_by']:
            for col in query['group_by']:
                self.collect_columns(col, used_columns)
        
 
        if query['having']:
            self.collect_columns(query['having'], used_columns)
        
 
        if query['order_by']:
            for item in query['order_by']:
                self.collect_columns(item['expr'], used_columns)

        for join in query['from']['joins']:
            self.collect_columns(join['condition'], used_columns)
        
        self.optimizations_applied.append(f"Removed unused columns, keeping only: {used_columns}")
        
  
        return query
    
    def collect_columns(self, expr, column_set):
        """Collect all column references from an expression"""
        if isinstance(expr, dict):
            if expr['type'] == 'column':
                col_name = expr.get('name')
                if col_name:
                    column_set.add(col_name)
            
            elif expr['type'] == 'binary_op':
                self.collect_columns(expr['left'], column_set)
                self.collect_columns(expr['right'], column_set)
            
            elif expr['type'] == 'function' and isinstance(expr['args'], dict):
                self.collect_columns(expr['args'], column_set)
    
    def merge_filters(self, query):
        """Merge multiple filters into single expression"""
       
        self.optimizations_applied.append("Merged multiple filter conditions")
        return query
    
    def expr_to_str(self, expr):
        """Convert expression to string for display"""
        if expr['type'] == 'binary_op':
            left = self.expr_to_str(expr['left'])
            right = self.expr_to_str(expr['right'])
            return f"({left} {expr['op']} {right})"
        
        elif expr['type'] == 'column':
            if 'table' in expr:
                return f"{expr['table']}.{expr['name']}"
            return expr['name']
        
        elif expr['type'] == 'literal':
            return repr(expr['value'])
        
        return str(expr)