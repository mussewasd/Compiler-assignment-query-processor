"""
planner.py - Query plan generator with intermediate representation
"""

class Planner:
    """Generates query execution plans"""
    
    def create_plan(self, optimized_query):
        """Create execution plan from optimized query"""
        plan = {
            'type': 'QUERY_PLAN',
            'steps': [],
            'cost_estimate': 0,
            'cardinality_estimate': 0
        }
        
     
        table_plan = self.plan_table_access(optimized_query['from'])
        plan['steps'].extend(table_plan['steps'])
        plan['cost_estimate'] += table_plan['cost']
        plan['cardinality_estimate'] = table_plan['cardinality']
        

        if optimized_query['where']:
            filter_step = self.plan_filter(optimized_query['where'], table_plan['cardinality'])
            plan['steps'].append(filter_step)
            plan['cost_estimate'] += filter_step['cost']
            plan['cardinality_estimate'] = filter_step['output_cardinality']
        
       
        if 'pushed_filters' in optimized_query:
            for filter_cond in optimized_query['pushed_filters']:
                filter_step = self.plan_filter(filter_cond, plan['cardinality_estimate'])
                plan['steps'].append(filter_step)
                plan['cost_estimate'] += filter_step['cost']
                plan['cardinality_estimate'] = filter_step['output_cardinality']
        
      
        if optimized_query['group_by']:
            group_step = self.plan_group_by(optimized_query['group_by'], 
                                           optimized_query['columns'],
                                           plan['cardinality_estimate'])
            plan['steps'].append(group_step)
            plan['cost_estimate'] += group_step['cost']
            plan['cardinality_estimate'] = group_step['output_cardinality']
        
      
        if optimized_query['having']:
            having_step = self.plan_having(optimized_query['having'], plan['cardinality_estimate'])
            plan['steps'].append(having_step)
            plan['cost_estimate'] += having_step['cost']
            plan['cardinality_estimate'] = having_step['output_cardinality']
        
        
        project_step = self.plan_projection(optimized_query['columns'], plan['cardinality_estimate'])
        plan['steps'].append(project_step)
        plan['cost_estimate'] += project_step['cost']
        
     
        if optimized_query['order_by']:
            sort_step = self.plan_sort(optimized_query['order_by'], plan['cardinality_estimate'])
            plan['steps'].append(sort_step)
            plan['cost_estimate'] += sort_step['cost']
        

        if optimized_query['limit']:
            limit_step = self.plan_limit(optimized_query['limit'], plan['cardinality_estimate'])
            plan['steps'].append(limit_step)
            plan['cost_estimate'] += limit_step['cost']
            plan['cardinality_estimate'] = limit_step['output_cardinality']
        
        return plan
    
    def plan_table_access(self, from_clause):
        """Plan table access operations"""
        plan = {'steps': [], 'cost': 0, 'cardinality': 0}
        
      
        main_table = from_clause['table']
        step = {
            'type': 'TABLE_SCAN',
            'table': main_table['name'],
            'alias': main_table.get('alias'),
            'cost': 100,
            'output_cardinality': 1000, 
            'filter': None
        }
        plan['steps'].append(step)
        plan['cost'] += step['cost']
        plan['cardinality'] = step['output_cardinality']
        
        
        for join in from_clause['joins']:
            join_step = {
                'type': f'{join["type"]}_JOIN',
                'left_input': f"step_{len(plan['steps']) - 1}",
                'right_table': join['table']['name'],
                'condition': join['condition'],
                'cost': 500,
                'output_cardinality': plan['cardinality'] * 100  
            }
            plan['steps'].append(join_step)
            plan['cost'] += join_step['cost']
            plan['cardinality'] = join_step['output_cardinality']
        
        return plan
    
    def plan_filter(self, condition, input_cardinality):
        """Plan filter operation"""
        return {
            'type': 'FILTER',
            'condition': condition,
            'cost': input_cardinality * 0.1,  
            'output_cardinality': int(input_cardinality * 0.3),  
            'selectivity': 0.3
        }
    
    def plan_group_by(self, group_by, select_columns, input_cardinality):
        """Plan GROUP BY operation"""
        
        use_hash = input_cardinality < 10000  
        
        aggregations = []
        for col in select_columns:
            if col['type'] == 'function':
                aggregations.append({
                    'function': col['name'],
                    'arg': col['args']
                })
        
        return {
            'type': 'HASH_AGGREGATE' if use_hash else 'SORT_AGGREGATE',
            'group_by': group_by,
            'aggregations': aggregations,
            'cost': input_cardinality * 2 if use_hash else input_cardinality * 3,
            'output_cardinality': int(input_cardinality * 0.1),  
            'method': 'hash' if use_hash else 'sort'
        }
    
    def plan_having(self, condition, input_cardinality):
        """Plan HAVING filter"""
        return {
            'type': 'HAVING_FILTER',
            'condition': condition,
            'cost': input_cardinality * 0.05,
            'output_cardinality': int(input_cardinality * 0.7)  
        }
    
    def plan_projection(self, columns, input_cardinality):
        """Plan projection (column selection)"""
        selected_columns = []
        for col in columns:
            if col['type'] == 'all':
                selected_columns.append('*')
            elif col['type'] == 'column':
                selected_columns.append(col.get('alias') or col['name'])
            elif col['type'] == 'function':
                selected_columns.append(col.get('alias') or f"{col['name']}(...)")
        
        return {
            'type': 'PROJECTION',
            'columns': selected_columns,
            'cost': input_cardinality * 0.01,
            'output_cardinality': input_cardinality
        }
    
    def plan_sort(self, order_by, input_cardinality):
        """Plan ORDER BY operation"""
        order_exprs = []
        for item in order_by:
            order_exprs.append({
                'expr': item['expr'],
                'direction': item['direction']
            })
        
        return {
            'type': 'SORT',
            'order_by': order_exprs,
            'cost': input_cardinality * 5,  
            'output_cardinality': input_cardinality,
            'method': 'quick_sort'
        }
    
    def plan_limit(self, limit, input_cardinality):
        """Plan LIMIT operation"""
        limit_value = int(limit)
        return {
            'type': 'LIMIT',
            'limit': limit_value,
            'cost': input_cardinality * 0.001,
            'output_cardinality': min(limit_value, input_cardinality)
        }