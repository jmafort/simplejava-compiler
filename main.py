import os

from compiler.lexical_analyzer import LexicalAnalyzer
from compiler.syntactic_analyzer import SyntacticAnalyzer


lex = LexicalAnalyzer()
lex.build()

yacc = SyntacticAnalyzer()
yacc.build()

directory = 'simple-java-programs'
simplejava_program_file_list = [os.path.join(directory, filename) for filename in os.listdir(directory) if filename.endswith('.sjava')]

for simplejava_program_file in simplejava_program_file_list:
    with open(simplejava_program_file, 'r') as simplejava_program:
        print(f"----{simplejava_program.name}----\n")
        tree = yacc.parse(simplejava_program.read())
        print(tree.__repr__())
