from typing import Counter

from ply import lex
from ply.lex import LexToken


class LexicalAnalyzer:
     
    tokens = [ 
        'DOUBLEPLUS',
        'PLUS',
        'DOUBLEMINUS',
        'MINUS',
        'TIMES',
        'DIVIDE',
        'MORETHAN',
        'LESSTHAN',
        'MOREOREQUALTHAN',
        'LESSOREQUALTHAN',
        'DOUBLEEQUALS',
        'NOTEQUAL',
        'ASSIGNMENT',
        'COLON',
        'DOT',
        'COMMA',
        'SEMICOLON',
        'LPAREN',
        'RPAREN',
        'LSBRACKET',
        'RSBRACKET',
        'LCURLYBRACE',
        'RCURLYBRACE',
        'STRING',
        'CHARACTER',
        'NUMBER',
        'TRUE',
        'FALSE',
        'ID',
        'WHITE_SPACE'
    ]

    reserved_words = [
        "CLASS",
        "INTERFACE",
        "ABSTRACT",
        "CONCRETE",
        "EXTENDS",
        "IMPLEMENTS",
        "PUBLIC",
        "PROTECTED",
        "PRIVATE",
        "STATIC",
        "LOCAL",
        "FINAL",
        "BASE",
        "INT",
        "FLOAT",
        "DOUBLECHAR",
        "VOID",
        "WHILE",
        "DO",
        "IF",
        "FOR",
        "SWITCH",
        "BREAK",
        "CONTINUE",
        "RETURN",
        "ELSE",
        "CASE",
        "DEFAULT",
        "NEW",
        "THIS"
    ]

    tokens += reserved_words

    t_NUMBER = r"(\d)+\.?(\d)*"
    t_DOUBLEPLUS = r'\+\+'
    t_PLUS = r'\+'
    t_DOUBLEMINUS = r'--'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_DIVIDE = r'/'
    t_MORETHAN = r'>'
    t_LESSTHAN = r'<'
    t_MOREOREQUALTHAN = r'=>'
    t_LESSOREQUALTHAN = r'<='
    t_DOUBLEEQUALS = r'=='
    t_NOTEQUAL = r'!='
    t_ASSIGNMENT = r'='
    t_COLON = r':'
    t_DOT = r'\.' 
    t_COMMA = r','
    t_SEMICOLON = r';'
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_LSBRACKET = r'\['
    t_RSBRACKET = r'\]'
    t_LCURLYBRACE = r'\{'
    t_RCURLYBRACE = r'\}'
    t_TRUE = r'true'
    t_FALSE = r'false'

    def __init__(self):
        """
        Building a stat tracker.
        """

        self.comments: int = 0
        self.unique_token_types: Counter = Counter()

    def t_COMMENT_INLINE(self, token) -> None:
        r"//(.)*(\n)?"
        
        self.comments += 1
    
    @staticmethod
    def t_WHITE_SPACE(token) -> None:
        r"\ |\f|\r|\t|\v"
        
    @staticmethod
    def t_NEWLINE(token) -> None:
        r"\n+"
        
        token.lexer.lineno += len(token.value)

    # def t_NUMBER(self, token) -> LexToken:
    #     r"\d+(\.\d+)?"

    #     token.value = int(token.value) if not "." in token.value else float(token.value)
    #     self.unique_token_types["NUMBER"] += 1
    #     return token
        
    def t_ID(self, token):
        r"[a-zA-Z][a-zA-Z_0-9]*"

        if token.value.upper() in self.reserved_words:
            token.type = token.value.upper()
            self.unique_token_types[token.type] += 1
        
        return token

    def t_STRING(self, token) -> LexToken:
        r"\"([^\"\n\0]*)\""

        self.unique_token_types["STRING"] += 1
        return token
    
    def t_CHARACTER(self, token) -> LexToken:
        r"'.'"
        self.unique_token_types["CHARACTER"] += 1
        return token

    @staticmethod
    def t_error(token) -> None:
        print(f'Illegal character: [{token.value[0]}]')
        token.lexer.skip(1)

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
        return self
    
    def parse(self, data) -> None:
        self.lexer.input(data)
        
        while True:
            token = self.lexer.token()
            if not token:
                break
            
            print(token)

        print(
            '\n'
            f'COMMENTS found: {self.comments}\n'
            f'Unique TOKEN TYPES found: {self.unique_token_types}'
            '\n'
        )
