class SemanticAnalyzer:
    def __init__(self):
        """
        Initialize the symbol table with the following structure:
        Nome     | classificação | tipo | escopo   | Qtd  | ordem
        Fatorial | função        | void | Global   |  1   | None
        x        | parâmetro     | int  | Fatorial | None | 1
        
        Symbol table is a dictionary of dictionaries, where the key is: `(name_of_the_symbol, scope)`.
        """

        self.symbol_table = {}
        self.current_scope = "global"
        self.visited = dict()

    def depth_first_seach(self, node = None, *args, **kwargs):
        if node is None:
            return
        
        if node in self.visited:
            return
        
        self.visited[node] = True

        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        visitor(node, *args, **kwargs)

        for child in node.children:
            # Regra 2: Checa todos os ID's utilizados no programa até agora para ver se já foram declarados na tabela de simbolos
            if type(child).__name__ == 'ID':
                key = (child.value, self.current_scope)
                if key not in self.symbol_table:
                    raise Exception(f"ID [{child.value}] não declarado para o escopo [{self.current_scope}]")
            self.depth_first_seach(child, *args, **kwargs)

    def generic_visit(self, node, *args, **kwargs):
        pass

    def visit_declaration(self, node):
        # Adiciona o método na tabela de simbolos
        class_name = node.value
        method_or_attribute = node.children[4].children[3].children[1]
        if method_or_attribute.value == 'method_decl':
            method_name = method_or_attribute.children[2].value
            method_type = method_or_attribute.children[1].value
            self.add_symbol(method_name, 'metodo', method_type, None, None, class_name)

            # Adiciona os argumentos do método na tabela de simbolos
            for argument in node.children[4].children[3].children[1].children[3].children:
                last_scope = self.current_scope
                self.current_scope = method_name

                argument_name = argument.children[1].children[0].value
                argument_type = argument.children[0].value
                self.add_symbol(argument_name, 'argument', argument_type, None, None, method_name)
        
            # Adiciona as variaveis locais do método na tabela de simbolos
            for local_variable in node.children[4].children[3].children[1].children[5].children:
                local_variable_name = local_variable.children[1].children[0].value
                local_variable_type = local_variable.children[0].value
                self.add_symbol(local_variable_name, 'variavel', local_variable_type, None, None, method_name)
            
            self.current_scope = last_scope

        # Adiciona variaveis de classe na tabela de simbolos
        elif method_or_attribute.value == 'atrib_decl':
            attribute_name = method_or_attribute.children[1].children[0].value
            attribute_type = method_or_attribute.children[0].value
            self.add_symbol(attribute_name, 'variavel', attribute_type, None, None, class_name)

    def add_symbol(self, name, classification, type, qty, order, scope = None):
        key = (name, scope or self.current_scope)
        
        # Regra 1: Verifica se o ID já foi declarado no escopo atual, pois não é permitido declarar duas variáveis com o mesmo nome no mesmo escopo
        if key in self.symbol_table:
            raise Exception(f"ID [{name}] já declarado para o escopo [{self.current_scope}]")
        self.symbol_table[key] = {
            "classification": classification,
            "type": type,
            "qty": qty,
            "order": order
        }

        print(self.symbol_table)
        print('\n')