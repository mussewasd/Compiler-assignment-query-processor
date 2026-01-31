"""
parser.py - Fixed SQL parser with JOIN and GROUP BY support
"""

from lexer import Lexer

class Parser:
    """SQL parser that builds Abstract Syntax Tree (AST)"""
    
    def __init__(self):
        self.tokens = []
        self.pos = 0
        self.current_token = None
    
    def parse(self, query):
        """Parse SQL query into AST"""
        lexer = Lexer()
        self.tokens = lexer.tokenize(query)
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None
        
        return self.parse_select()
    
    def eat(self, token_type=None, token_value=None):
        """Consume current token if it matches expected type/value"""
        if not self.current_token:
            raise SyntaxError(f"Unexpected end of query")
        
        if token_type and self.current_token[0] != token_type:
            raise SyntaxError(f"Expected {token_type}, got {self.current_token[0]} at position {self.pos}")
        if token_value and self.current_token[1].upper() != token_value.upper():
            raise SyntaxError(f"Expected {token_value}, got {self.current_token[1]} at position {self.pos}")
        
        token = self.current_token
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
        
        return token
    
    def peek(self):
        """Look ahead one token"""
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return None
    
 
    
    def parse_select(self):
        """SELECT [DISTINCT] columns FROM tables [WHERE] [GROUP BY] [HAVING] [ORDER BY]"""
     
        self.eat('KEYWORD', 'SELECT')
        

        distinct = False
        if self.current_token and self.current_token[1] == 'DISTINCT':
            self.eat('KEYWORD', 'DISTINCT')
            distinct = True
        
        
        columns = self.parse_column_list()
        

        self.eat('KEYWORD', 'FROM')
        from_clause = self.parse_from_clause()
        
       
        where = None
        if self.current_token and self.current_token[1] == 'WHERE':
            self.eat('KEYWORD', 'WHERE')
            where = self.parse_expression()
        
     
        group_by = None
        if self.current_token and self.current_token[1] == 'GROUP':
            self.eat('KEYWORD', 'GROUP')
            self.eat('KEYWORD', 'BY')
            group_by = self.parse_column_list()
        
       
        having = None
        if self.current_token and self.current_token[1] == 'HAVING':
            self.eat('KEYWORD', 'HAVING')
            having = self.parse_expression()
        
     
        order_by = None
        if self.current_token and self.current_token[1] == 'ORDER':
            self.eat('KEYWORD', 'ORDER')
            self.eat('KEYWORD', 'BY')
            order_by = self.parse_order_by_list()
        
 
        limit = None
        if self.current_token and self.current_token[1] == 'LIMIT':
            self.eat('KEYWORD', 'LIMIT')
            limit = int(self.eat('NUMBER')[1])
        
        return {
            'type': 'SELECT',
            'distinct': distinct,
            'columns': columns,
            'from': from_clause,
            'where': where,
            'group_by': group_by,
            'having': having,
            'order_by': order_by,
            'limit': limit
        }
    
    def parse_from_clause(self):
        """Parse FROM clause with possible JOINs"""
     
        table = self.parse_table_reference()
        
      
        joins = []
        while self.current_token and self.current_token[1] in ('JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL'):
            join_type = 'INNER'
            if self.current_token[1] in ('LEFT', 'RIGHT', 'FULL'):
                join_type = self.eat('KEYWORD')[1]
                if self.current_token and self.current_token[1] == 'OUTER':
                    self.eat('KEYWORD')
            
            if self.current_token and self.current_token[1] == 'JOIN':
                self.eat('KEYWORD', 'JOIN')
            
            right_table = self.parse_table_reference()
            self.eat('KEYWORD', 'ON')
            condition = self.parse_expression()
            
            joins.append({
                'type': join_type,
                'table': right_table,
                'condition': condition
            })
        
        return {
            'table': table,
            'joins': joins
        }
    
    def parse_table_reference(self):
        """Parse table name with optional alias"""
        table_name = self.eat('ID')[1].upper()
        
        alias = None
        if self.current_token and self.current_token[1] == 'AS':
            self.eat('KEYWORD', 'AS')
            alias = self.eat('ID')[1].upper()
        elif self.current_token and self.current_token[0] == 'ID':
         
            alias = self.eat('ID')[1].upper()
        
        return {'type': 'table', 'name': table_name, 'alias': alias}
    
    def parse_column_list(self):
        """Parse list of columns or expressions"""
        columns = []
        
        while True:
            columns.append(self.parse_column_expression())
            
            if self.current_token and self.current_token[1] == ',':
                self.eat('COMMA')
            else:
                break
        
        return columns
    
    def parse_column_expression(self):
        """Parse a column expression (could be column, function, or expression)"""
      
        if self.current_token and self.current_token[1] in ('COUNT', 'SUM', 'AVG', 'MIN', 'MAX'):
            func_name = self.eat('KEYWORD')[1]
            self.eat('LPAREN')
            
            if self.current_token and self.current_token[0] == 'STAR':
                expr = {'type': 'all'}
                self.eat('STAR')
            elif self.current_token and self.current_token[1] == 'DISTINCT':
                self.eat('KEYWORD', 'DISTINCT')
                expr = self.parse_expression()
            else:
                expr = self.parse_expression()
            
            self.eat('RPAREN')
            
           
            alias = None
            if self.current_token and self.current_token[1] == 'AS':
                self.eat('KEYWORD', 'AS')
                alias = self.eat('ID')[1].upper()
            
            return {
                'type': 'function',
                'name': func_name,
                'args': expr,
                'alias': alias
            }
        
  
        if self.current_token and self.current_token[0] == 'STAR':
            self.eat('STAR')
            return {'type': 'all'}
        
       
        expr = self.parse_expression()
        
       
        alias = None
        if self.current_token and self.current_token[1] == 'AS':
            self.eat('KEYWORD', 'AS')
            alias = self.eat('ID')[1].upper()
        
        if alias:
            expr['alias'] = alias
        
        return expr
    
    def parse_expression(self):
        """Parse a boolean expression"""
        return self.parse_or_expression()
    
    def parse_or_expression(self):
        """Parse OR expressions"""
        expr = self.parse_and_expression()
        
        while self.current_token and self.current_token[1] == 'OR':
            self.eat('KEYWORD', 'OR')
            right = self.parse_and_expression()
            expr = {'type': 'binary_op', 'op': 'OR', 'left': expr, 'right': right}
        
        return expr
    
    def parse_and_expression(self):
        """Parse AND expressions"""
        expr = self.parse_comparison()
        
        while self.current_token and self.current_token[1] == 'AND':
            self.eat('KEYWORD', 'AND')
            right = self.parse_comparison()
            expr = {'type': 'binary_op', 'op': 'AND', 'left': expr, 'right': right}
        
        return expr
    
    def parse_comparison(self):
        """Parse comparison expressions including IS NULL/IS NOT NULL"""
        expr = self.parse_term()
        
        if self.current_token and self.current_token[0] == 'COMPARE':
            op = self.eat('COMPARE')[1]
            right = self.parse_term()
            return {'type': 'binary_op', 'op': op, 'left': expr, 'right': right}
        
        # Handle IS NULL / IS NOT NULL
        elif self.current_token and self.current_token[1] == 'IS':
            self.eat('KEYWORD', 'IS')
            
            not_null = False
            if self.current_token and self.current_token[1] == 'NOT':
                self.eat('KEYWORD', 'NOT')
                not_null = True
            
            self.eat('KEYWORD', 'NULL')
            

            if not_null:
                return {'type': 'binary_op', 'op': '!=', 'left': expr, 'right': {'type': 'literal', 'value': None}}
            else:
                return {'type': 'binary_op', 'op': '=', 'left': expr, 'right': {'type': 'literal', 'value': None}}
        
        return expr
    
    def parse_term(self):
        """Parse arithmetic terms"""
        expr = self.parse_factor()
        
        while self.current_token and self.current_token[1] in ('+', '-'):
            op = self.eat('OP')[1]
            right = self.parse_factor()
            expr = {'type': 'binary_op', 'op': op, 'left': expr, 'right': right}
        
        return expr
    
    def parse_factor(self):
        """Parse arithmetic factors"""
        expr = self.parse_primary()
        
        while self.current_token and self.current_token[1] in ('*', '/'):
            op = self.eat('OP')[1]
            right = self.parse_primary()
            expr = {'type': 'binary_op', 'op': op, 'left': expr, 'right': right}
        
        return expr
    
    def parse_primary(self):
        """Parse primary expressions: column, literal, or subquery"""
        if not self.current_token:
            raise SyntaxError("Unexpected end of query")
        
        if self.current_token[0] == 'NUMBER':
            value = self.eat('NUMBER')[1]
            return {'type': 'literal', 'value': float(value) if '.' in value else int(value)}
        
        elif self.current_token[0] == 'STRING':
            value = self.eat('STRING')[1]
            return {'type': 'literal', 'value': value[1:-1]}  
        
        elif self.current_token[1] == '(':
            self.eat('LPAREN')
            expr = self.parse_expression()
            self.eat('RPAREN')
            return expr
        
        else:
            
            parts = []
            while True:
                if self.current_token and self.current_token[0] == 'ID':
                    parts.append(self.eat('ID')[1].upper())  
                    if self.current_token and self.current_token[1] == '.':
                        self.eat('DOT')
                    else:
                        break
                else:
                    break
            
            if len(parts) == 1:
                return {'type': 'column', 'name': parts[0]}
            else:
                return {'type': 'column', 'table': parts[0], 'name': parts[1]}
    
    def parse_order_by_list(self):
        """Parse ORDER BY clause"""
        order_items = []
        
        while True:
            expr = self.parse_expression()
            direction = 'ASC'
            
            if self.current_token and self.current_token[1] in ('ASC', 'DESC'):
                direction = self.eat('KEYWORD')[1]
            
            order_items.append({'expr': expr, 'direction': direction})
            
            if self.current_token and self.current_token[1] == ',':
                self.eat('COMMA')
            else:
                break
        
        return order_items