from basic.lexer import Lexer
from basic.prsr import Parser
from basic.interpreter import Interpreter
from basic.context import Context
from basic.symbol_table import SymbolTable
from basic.number import Number

global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number(0), protected=True)
global_symbol_table.set("TRUE", Number(1), protected=True)
global_symbol_table.set("FALSE", Number(0), protected=True)

def run(fn, text):
  if text == "":
    return None, None

  # Get tokens
  lexer = Lexer(fn, text)
  tokens, error = lexer.make_tokens()
  if error: return None, error

  # Parse tokens
  parser = Parser(tokens)
  ast = parser.parse()
  if ast.error: return None, ast.error

  # Interpret nodes
  interpreter = Interpreter()
  context = Context("<program>")
  context.symbol_table = global_symbol_table
  result = interpreter.visit(ast.node, context)

  return result.value, result.error