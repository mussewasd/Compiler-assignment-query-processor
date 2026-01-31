"""
lexer.py - Fixed SQL lexer/tokenizer
"""

import re

class Lexer:
    """SQL lexer that tokenizes query strings"""
    
    def __init__(self):
        # SQL keywords - case insensitive
        self.keywords = {
            'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL',
            'ON', 'GROUP', 'BY', 'HAVING', 'ORDER', 'ASC', 'DESC', 'LIMIT',
            'AND', 'OR', 'NOT', 'AS', 'IN', 'IS', 'NULL', 'DISTINCT',
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'ALL', 'ANY'
        }
        

        self.token_specification = [
            ('NUMBER',    r'\d+(\.\d*)?'),      # Integer or decimal
            ('STRING',    r"'[^']*'"),          # Single quoted strings
            ('STAR',      r'\*'),               # Asterisk for SELECT *
            ('ID',        r'[A-Za-z_][A-Za-z0-9_]*'),  # Identifiers
            ('COMMA',     r','),                # Comma
            ('DOT',       r'\.'),               # Dot
            ('OP',        r'[+\-*/]'),          # Arithmetic operators
            ('COMPARE',   r'[=<>!]=?'),         # Comparison operators
            ('LPAREN',    r'\('),               # Left paren
            ('RPAREN',    r'\)'),               # Right paren
            ('SKIP',      r'[ \t]+'),           # Skip spaces/tabs
            ('NEWLINE',   r'\n'),               # Line endings
            ('MISMATCH',  r'.'),                # Any other character
        ]
        
        self.token_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in self.token_specification)
    
    def tokenize(self, text):
        """Convert SQL text into tokens - preserve original case for IDs"""
        tokens = []
        
        for mo in re.finditer(self.token_regex, text):
            kind = mo.lastgroup
            value = mo.group()
            
            if kind == 'SKIP' or kind == 'NEWLINE':
                continue
            elif kind == 'MISMATCH':
                raise SyntaxError(f'Unexpected character: {value}')
            elif kind == 'ID' and value.upper() in self.keywords:
                kind = 'KEYWORD'
                value = value.upper() 
            
            tokens.append((kind, value))
        
        return tokens