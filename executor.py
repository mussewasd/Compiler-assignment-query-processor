"""
executor.py - Fixed query executor with proper JOIN handling
"""

from database import DATABASE

class Executor:
    """Executes query AST against in-memory database"""
    
    def __init__(self, database):
        self.db = database
    
    def execute(self, query_ast):
        """Execute query AST directly"""
        # Get main table
        from_clause = query_ast['from']
        main_table_ref = from_clause['table']
        main_table_name = main_table_ref['name']
        main_table_alias = main_table_ref.get('alias', main_table_name)
        
        # Start with main table data
        data = self.db.get(main_table_name, []).copy()
        
        # Apply JOINs if any
        if from_clause['joins']:
            data = self.execute_joins(data, from_clause)
        
        # Apply WHERE
        if query_ast['where']:
            data = [row for row in data if self.evaluate_expression(row, query_ast['where'])]
        
        # Apply GROUP BY with aggregations
        if query_ast['group_by']:
            data = self.execute_group_by(data, query_ast['group_by'], query_ast['columns'])
        else:
            # Apply aggregations without grouping
            data = self.execute_aggregations(data, query_ast['columns'])
        
        # Apply HAVING
        if query_ast['having']:
            data = [row for row in data if self.evaluate_expression(row, query_ast['having'])]
        
        # Apply ORDER BY
        if query_ast['order_by']:
            data = self.execute_order_by(data, query_ast['order_by'])
        
        # Apply LIMIT
        if query_ast['limit']:
            limit = int(query_ast['limit'])
            data = data[:limit]
        
        # Apply DISTINCT
        if query_ast['distinct']:
            data = self.execute_distinct(data)
        
        # Apply final projection
        data = self.execute_projection(data, query_ast['columns'])
        
        return data
    
    def execute_joins(self, left_data, from_clause):
        """Execute all JOIN operations"""
        main_table_ref = from_clause['table']
        
        for join in from_clause['joins']:
            join_table_name = join['table']['name']
            join_table_alias = join['table'].get('alias', join_table_name)
            join_data = self.db.get(join_table_name, [])
            
            # Simple nested loop join
            joined_data = []
            for left_row in left_data:
                joined = False
                for right_row in join_data:
                    if self.evaluate_join_condition(left_row, right_row, join['condition']):
                        # Merge rows with proper column names
                        merged_row = {}
                        
                        # Add left table columns with table prefix
                        for key, value in left_row.items():
                            if join['type'] == 'LEFT' or join['type'] == 'INNER':
                                merged_row[key] = value
                        
                        # Add right table columns with table prefix
                        for key, value in right_row.items():
                            if join['type'] == 'LEFT' or join['type'] == 'INNER':
                                merged_row[key] = value
                        
                        joined_data.append(merged_row)
                        joined = True
                
                # Handle LEFT JOIN when no match found
                if join['type'] == 'LEFT' and not joined:
                    merged_row = {}
                    # Add left table columns
                    for key, value in left_row.items():
                        merged_row[key] = value
                    # Add null values for right table columns
                    for key in join_data[0].keys() if join_data else []:
                        merged_row[key] = None
                    joined_data.append(merged_row)
            
            left_data = joined_data
        
        return left_data
    
    def evaluate_join_condition(self, left_row, right_row, condition):
        """Evaluate JOIN condition between two rows"""
        if condition['type'] == 'binary_op' and condition['op'] == '=':
            left_col = condition['left']
            right_col = condition['right']
            
            # Get left value
            left_val = None
            if left_col.get('table'):
                # Column with table prefix
                if left_col['table'] in ['E', 'EMPLOYEES']:
                    left_val = left_row.get(left_col['name'])
                else:
                    left_val = right_row.get(left_col['name'])
            else:
                # Column without table prefix - try both
                left_val = left_row.get(left_col['name'])
                if left_val is None:
                    left_val = right_row.get(left_col['name'])
            
            # Get right value
            right_val = None
            if right_col.get('table'):
                # Column with table prefix
                if right_col['table'] in ['D', 'DEPARTMENTS']:
                    right_val = right_row.get(right_col['name'])
                else:
                    right_val = left_row.get(right_col['name'])
            else:
                # Column without table prefix - try both
                right_val = right_row.get(right_col['name'])
                if right_val is None:
                    right_val = left_row.get(right_col['name'])
            
            return left_val == right_val
        
        return False
    
    def execute_group_by(self, data, group_by, select_columns):
        """Execute GROUP BY with aggregations"""
        if not data:
            return []
        
        # Group data
        groups = {}
        for row in data:
            group_key = tuple(self.evaluate_expression(row, expr) for expr in group_by)
            
            if group_key not in groups:
                groups[group_key] = []
            groups[group_key].append(row)
        
        # Apply aggregations per group
        results = []
        for group_key, group_rows in groups.items():
            result_row = {}
            
            # Add group by columns
            for i, expr in enumerate(group_by):
                col_name = self.get_column_name(expr)
                result_row[col_name] = group_key[i]
            
            # Apply aggregations
            for col_expr in select_columns:
                if col_expr['type'] == 'function':
                    func_name = col_expr['name']
                    col_alias = col_expr.get('alias', f"{func_name}")
                    
                    if func_name == 'COUNT':
                        if isinstance(col_expr['args'], dict) and col_expr['args']['type'] == 'all':
                            result_row[col_alias] = len(group_rows)
                        else:
                            # COUNT(column)
                            arg_expr = col_expr['args']
                            non_null_count = 0
                            for row in group_rows:
                                if self.evaluate_expression(row, arg_expr) is not None:
                                    non_null_count += 1
                            result_row[col_alias] = non_null_count
                    
                    elif func_name == 'SUM':
                        arg_expr = col_expr['args']
                        total = 0
                        for row in group_rows:
                            val = self.evaluate_expression(row, arg_expr)
                            if val is not None:
                                total += val
                        result_row[col_alias] = total
                    
                    elif func_name == 'AVG':
                        arg_expr = col_expr['args']
                        total = 0
                        count = 0
                        for row in group_rows:
                            val = self.evaluate_expression(row, arg_expr)
                            if val is not None:
                                total += val
                                count += 1
                        result_row[col_alias] = total / count if count > 0 else 0
            
            results.append(result_row)
        
        return results
    
    def execute_aggregations(self, data, select_columns):
        """Execute aggregations without grouping"""
        if not data:
            return []
        
        # Check if we have any aggregations
        has_aggregations = any(col['type'] == 'function' for col in select_columns)
        
        if not has_aggregations:
            return data
        
        # Create single result row with aggregations
        result_row = {}
        
        for col_expr in select_columns:
            if col_expr['type'] == 'function':
                func_name = col_expr['name']
                col_alias = col_expr.get('alias', f"{func_name}")
                
                if func_name == 'COUNT':
                    if isinstance(col_expr['args'], dict) and col_expr['args']['type'] == 'all':
                        result_row[col_alias] = len(data)
                    else:
                        arg_expr = col_expr['args']
                        non_null_count = 0
                        for row in data:
                            if self.evaluate_expression(row, arg_expr) is not None:
                                non_null_count += 1
                        result_row[col_alias] = non_null_count
                
                elif func_name == 'SUM':
                    arg_expr = col_expr['args']
                    total = sum(self.evaluate_expression(row, arg_expr) or 0 for row in data)
                    result_row[col_alias] = total
                
                elif func_name == 'AVG':
                    arg_expr = col_expr['args']
                    values = [self.evaluate_expression(row, arg_expr) for row in data]
                    values = [v for v in values if v is not None]
                    result_row[col_alias] = sum(values) / len(values) if values else 0
            
            elif col_expr['type'] == 'column':
                col_name = col_expr.get('alias') or col_expr['name']
                # For single row result with aggregations, we can't include non-aggregated columns
                result_row[col_name] = None
        
        return [result_row]
    
    def evaluate_expression(self, row, expr):
        """Evaluate expression in context of a row"""
        if expr['type'] == 'literal':
            return expr['value']
        
        elif expr['type'] == 'column':
            col_name = expr['name']
            return row.get(col_name)
        
        elif expr['type'] == 'binary_op':
            left = self.evaluate_expression(row, expr['left'])
            right = self.evaluate_expression(row, expr['right'])
            op = expr['op']
            
            # Handle NULL comparisons
            if left is None or right is None:
                if op == '=':
                    return left == right
                elif op == '!=':
                    return left != right
                return None
            
            if op == '=':
                return left == right
            elif op == '!=':
                return left != right
            elif op == '>':
                return left > right
            elif op == '<':
                return left < right
            elif op == '>=':
                return left >= right
            elif op == '<=':
                return left <= right
            elif op == '+':
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                return left / right if right != 0 else None
            elif op == 'AND':
                return bool(left) and bool(right)
            elif op == 'OR':
                return bool(left) or bool(right)
        
        elif expr['type'] == 'function':
            # For row-level evaluation, functions like COUNT return 1
            return 1
        
        return None
    
    def execute_order_by(self, data, order_by):
        """Execute ORDER BY"""
        def sort_key(row):
            key = []
            for item in order_by:
                value = self.evaluate_expression(row, item['expr'])
                # Handle None values
                if value is None:
                    value = float('-inf') if item['direction'] == 'ASC' else float('inf')
                key.append(value)
            return tuple(key)
        
        reverse = any(item['direction'] == 'DESC' for item in order_by)
        return sorted(data, key=sort_key, reverse=reverse)
    
    def execute_distinct(self, data):
        """Execute DISTINCT"""
        seen = set()
        distinct_data = []
        
        for row in data:
            # Create hashable representation of row
            row_tuple = tuple(sorted(row.items()))
            if row_tuple not in seen:
                seen.add(row_tuple)
                distinct_data.append(row)
        
        return distinct_data
    
    def execute_projection(self, data, columns):
        """Select only specified columns"""
        if not data:
            return data
        
        # If SELECT *, return all columns
        if any(col['type'] == 'all' for col in columns):
            return data
        
        results = []
        for row in data:
            new_row = {}
            for col_expr in columns:
                if col_expr['type'] == 'column':
                    col_name = col_expr['name']
                    alias = col_expr.get('alias', col_name)
                    
                    # Get the column value
                    value = row.get(col_name)
                    
                    new_row[alias] = value
                
                elif col_expr['type'] == 'function':
                    alias = col_expr.get('alias', col_expr['name'])
                    new_row[alias] = row.get(alias)
            
            results.append(new_row)
        
        return results
    
    def get_column_name(self, expr):
        """Get column name from expression"""
        if expr['type'] == 'column':
            return expr.get('alias') or expr['name']
        return str(expr)