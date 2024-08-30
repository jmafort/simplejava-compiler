import ply.yacc as yacc
from compiler.lexical_analyzer import LexicalAnalyzer

class Node:
    def __init__(self, type, children=None, value=None):
        self.type = type
        self.children = children if children is not None else []
        self.value = value

    def __repr__(self):
        return self._repr()

    def _repr(self, level=0):
        ret = "   " * level + repr(self.type) + (f": {self.value}" if self.value else "") + "\n"
        for child in self.children:
            if isinstance(child, Node):
                ret += child._repr(level + 1)
        return ret

class SyntacticAnalyzer:
    tokens = LexicalAnalyzer.tokens

    precedence = (
        ('nonassoc', 'MORETHAN', 'LESSTHAN', 'MOREOREQUALTHAN', 'LESSOREQUALTHAN', 'DOUBLEEQUALS', 'NOTEQUAL'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('left', 'DOUBLEPLUS', 'DOUBLEMINUS'),
    )

    def p_program(self, p):
        """
        program : declaration declarations
        """
        p[0] = Node("program", [p[1], p[2]])

    def p_declarations(self, p):
        """
        declarations : declaration declarations
                     | empty
        """
        if p[1] is not None:
            p[0] = Node("declarations", [p[1], p[2]])

    def p_declaration(self, p):
        """
        declaration : struct ID inheritance LCURLYBRACE item_decls RCURLYBRACE
        """
        p[0] = Node("declaration", [p[1], Node("ID", value=p[2]), p[3], p[5]])

    def p_struct(self, p):
        """
        struct : instance CLASS
               | INTERFACE
        """
        if len(p) == 3:
            p[0] = Node("struct", [p[1]], value=p[2])
        elif len(p) == 2:
            p[0] = Node("struct", value=p[1])

    def p_instance(self, p):
        """
        instance : ABSTRACT
                 | CONCRETE
        """
        p[0] = Node("instance", value=p[1])

    def p_inheritance(self, p):
        """
        inheritance : EXTENDS ID
                    | IMPLEMENTS ID
                    | empty
        """
        if len(p) == 3:
            p[0] = Node("inheritance", [Node("ID", value=p[2])], value=p[1] + "(" + p[2] + ")")

    def p_item_decls(self, p):
        """
        item_decls : visibility scope final item_decl SEMICOLON item_decls
                   | empty
        """
        if p[1] is not None:
            p[0] = Node("item_decls", [p[1], p[2], p[3], p[4], p[6]])

    def p_visibility(self, p):
        """
        visibility : PUBLIC
                   | PROTECTED
                   | PRIVATE
        """
        p[0] = Node("visibility", value=p[1])

    def p_scope(self, p):
        """
        scope : STATIC
              | LOCAL
        """
        p[0] = Node("scope", value=p[1])

    def p_final(self, p):
        """
        final : FINAL
              | BASE
        """
        p[0] = Node("final", value=p[1])

    def p_item_decl(self, p):
        """
        item_decl : atrib_decl
                  | method_decl
        """
        p[0] = Node("item_decl", [p[1]])

    def p_atrib_decl(self, p):
        """
        atrib_decl : type var var_list SEMICOLON
        """
        p[0] = Node("atrib_decl", [p[1], p[2], p[3]])

    def p_method_decl(self, p):
        """
        method_decl : instance type method
        """
        p[0] = Node("method_decl", [p[1], p[2], p[3]])

    def p_type(self, p):
        """
        type : INT
             | FLOAT
             | DOUBLE
             | CHAR
             | VOID
             | ID value
        """
        if len(p) == 3:
            p[0] = Node("type", [Node("ID", value=p[1]), p[2]])
        elif len(p) == 2:
            p[0] = Node("type", value=p[1])

    def p_var(self, p):
        """
        var : ID array value
        """
        p[0] = Node("var", [Node("ID", value=p[1]) , p[2], p[3]])

    def p_value(self, p):
        """
        value : ASSIGNMENT exp
              | empty
        """
        if len(p) == 3:
            p[0] = Node("value", [p[2]])

    def p_var_list(self, p):
        """
        var_list : COMMA var var_list
                 | empty
        """
        if p[1] is not None:
            p[0] = Node("var_list", [p[2], p[3]])

    def p_array(self, p):
        """
        array : LSBRACKET RSBRACKET array
              | empty
        """
        if len(p) == 4:
            p[0] = Node("array", [p[3]])

    def p_method(self, p):
        """
        method : ID LPAREN argument RPAREN bloc_com
        """
        p[0] = Node("method", [Node("ID", value=p[1]), p[3], p[5]])

    def p_argument(self, p):
        """
        argument : type var arg_list
                 | empty
        """
        if p[1] is not None:
            p[0] = Node("argument", [p[1], p[2], p[3]])

    def p_arg_list(self, p):
        """
        arg_list : COMMA argument
                 | empty
        """
        if p[1] is not None:
            p[0] = Node("arg_list", [p[2]])
    
    def p_bloc_com(self, p):
        """
        bloc_com : LCURLYBRACE com_list RCURLYBRACE
        """
        p[0] = Node("bloc_com", [p[2]])
    
    def p_bloc(self, p):
        """
        bloc : bloc_com
             | command SEMICOLON
        """
        p[0] = Node("bloc_com", [p[1]])

    def p_com_list(self, p):
        """
        com_list : command com_list
                 | empty
        """
        if p[1] is not None:
            p[0] = Node("com_list", [p[1], p[2]])
    
    def p_command(self, p):
        """
        command : atrib SEMICOLON
                | WHILE LPAREN exp_logic RPAREN bloc
                | DO bloc WHILE LPAREN exp_logic RPAREN SEMICOLON
                | IF LPAREN exp_logic RPAREN bloc else
                | FOR LPAREN for_exp RPAREN bloc
                | SWITCH LPAREN ID name RPAREN LCURLYBRACE switch_case RCURLYBRACE
                | BREAK SEMICOLON
                | CONTINUE SEMICOLON
                | RETURN exp SEMICOLON
        """
        if p[1] == "while" or p[1] == "for":
            p[0] = Node("command", [p[3], p[5]], value=p[1])
        elif p[1] == "do":
            p[0] = Node("command", [p[2], p[5]], value=p[1])
        elif p[1] == "if":
            p[0] = Node("command", [p[3], p[5], p[6]], value=p[1])
        elif p[1] == "switch":
            p[0] = Node("command", [p[4], p[7]], value=p[1])
        elif p[1] == "break" or p[1] == "continue":
            p[0] = Node("command", value=p[1])
        elif p[1] == "return":
            p[0] = Node("command", [p[2]], value=p[1])
        else:
            p[0] = Node("command", [p[1]], value="ATRIB")

    def p_atrib(self, p):
        """
        atrib : ID name ASSIGNMENT exp
        """
        p[0] = Node("atrib", [Node("ID", value=p[1]), p[2], p[4]])

    def p_else(self, p):
        """
        else : ELSE bloc
             | empty
        """
        if len(p) == 3:
            p[0] = Node("else", [p[2]])

    def p_for_exp(self, p):
        """
        for_exp : atrib_decl SEMICOLON exp_logic SEMICOLON atrib
                | type ID COLON ID name
        """
        if p[3] == "colon":
            p[0] = Node("for_exp", [p[1], Node("ID", value=p[2]), Node("ID", value=p[4]), p[5]])
        else:
            p[0] = Node("for_exp", [p[1], p[3], p[5]])

    def p_switch_case(self, p):
        """
        switch_case : CASE const COLON bloc switch_case
                    | DEFAULT bloc
        """
        if p[1] == "case":
            p[0] = Node("switch_case", [p[2], p[4], p[5]], value=p[1])
        else:
            p[0] = Node("switch_case", [p[2]], value=p[1])

    def p_exp(self, p):
        """
        exp : exp_math
            | exp_logic
            | operator ID name
            | NEW type name
        """
        if len(p) == 2:
            p[0] = Node("exp", [p[1]])
        elif len(p) == 4 and p[1] == "new":
            p[0] = Node("exp", [p[2], p[3]])
        else:
            p[0] = Node("exp", [p[1], Node("ID", value=p[2]), p[3]])

    def p_operator(self, p):
        """
        operator : DOUBLEPLUS
                 | DOUBLEMINUS
        """
        p[0] = Node("operator", value=p[1])

    def p_params(self, p):
        """
        params : param param_list
               | empty
        """
        if len(p) == 4:
            p[0] = Node("params", [p[1], p[2]])
    
    def p_param_list(self, p):
        """
        param_list : COMMA param param_list
                   | empty
        """
        if p[1] is not None:
            p[0] = Node("param_list", [p[2], p[3]])
    
    def p_exp_logic(self, p):
        """
        exp_logic : exp_math op_logic exp_logic_tail
                  | operator ID name op_logic exp_logic_tail
                  | NEW type name op_logic exp_logic_tail
                  | exp_logic_tail
        """
        if len(p) == 4:
            p[0] = Node("exp_logic", [p[1], p[2], p[3]])
        elif len(p) == 6 and p[1] == "new":
            p[0] = Node("exp_logic", [p[2], p[3], p[4], p[5]])
        elif len(p) == 6:
            p[0] = Node("exp_logic", [p[1], Node("ID", value=p[2]), p[3], p[4], p[5]])
        else:
            p[0] = Node("exp_logic", [p[1]])

    def p_exp_logic_tail(self, p):
        """
        exp_logic_tail : exp_math
                       | empty
        """
        if len(p) == 3:
            p[0] = Node("exp_logic_tail", [p[1], p[2]])

    def p_exp_math(self, p):
        """
        exp_math : param op_math exp_math
                 | param
        """
        if len(p) == 4:
            p[0] = Node("exp_math", [p[1], p[2], p[3]])
        elif len(p) == 2:
            p[0] = Node("exp_math", [p[1]])

    def p_op_logic(self, p):
        """
        op_logic : MORETHAN
                 | LESSTHAN
                 | MOREOREQUALTHAN
                 | LESSOREQUALTHAN
                 | DOUBLEEQUALS
                 | NOTEQUAL
        """
        p[0] = Node("op_logic", value=p[1])

    def p_op_math(self, p):
        """
        op_math : PLUS
                | MINUS
                | TIMES
                | DIVIDE
        """
        p[0] = Node("op_math", value=p[1])
    
    def p_param(self, p):
        """
        param : ID name
              | THIS field
              | const
        """
        if len(p) == 3 and p[1] == "this":
            p[0] = Node("param", [p[2]], value=p[1])
        elif len(p) == 2:
            p[0] = Node("param", [p[1]])
        else:
            p[0] = Node("param", [Node("ID", value=p[1]), p[2]])

    def p_name(self, p):
        """
        name : field
            | array_size name_non_empty
            | LPAREN params RPAREN name_non_empty
            | empty
        """
        if len(p) == 2 and p[1] is not None:
            p[0] = Node("name", [p[1]])
        elif len(p) == 3:
            p[0] = Node("name", [p[1], p[2]])
        elif len(p) == 5:
            p[0] = Node("name", [p[2], p[4]])

    def p_name_non_empty(self, p):
        """
        name_non_empty : field
                    | array_size name_non_empty
                    | LPAREN params RPAREN name_non_empty
        """
        if len(p) == 2:
            p[0] = Node("name_non_empty", [p[1]])
        elif len(p) == 3:
            p[0] = Node("name_non_empty", [p[1], p[2]])
        elif len(p) == 5:
            p[0] = Node("name_non_empty", [p[2], p[4]])

    def p_field(self, p):
        """
        field : DOT ID name_non_empty
            | empty
        """
        if len(p) == 4:
            p[0] = Node("field", [Node("ID", value=p[2]), p[3]])

    def p_array_size(self, p):
        """
        array_size : LSBRACKET exp_math RSBRACKET array_size_non_empty
                | empty
        """
        if len(p) == 4:
            p[0] = Node("array_size", [p[2], p[4]])

    def p_array_size_non_empty(self, p):
        """
        array_size_non_empty : LSBRACKET exp_math RSBRACKET array_size_non_empty
                            | empty
        """
        if len(p) == 4:
            p[0] = Node("array_size_non_empty", [p[2], p[4]])
    
    def p_const(self, p):
        """
        const : NUMBER
              | STRING
              | CHARACTER
              | TRUE
              | FALSE
        """
        p[0] = Node("const", value=p[1])

    def p_error(self, p):
        print(f"\nSyntax error!\nLine: {p.lineno}\nToken: {p.value}\nType: {p.type}\n")

    def p_empty(self, p):
        """
        empty :
        """
        p[0] = None

    def build(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)
        return self

    def parse(self, data, **kwargs):
        return self.parser.parse(data, **kwargs)