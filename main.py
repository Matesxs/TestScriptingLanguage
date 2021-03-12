from lib import Lexer
from lib import Parser
from lib import Interpreter
from lib import Context
from lib import SymbolTable
from lib import Number
from lib import String

global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number(0), protected=True)
global_symbol_table.set("TRUE", Number(1), protected=True)
global_symbol_table.set("FALSE", Number(0), protected=True)
global_symbol_table.set("PICA", String("Svědiroh"), protected=True)

def run(fn, text):
  if text == "" or text == "\n":
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