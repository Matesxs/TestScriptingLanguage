from lib.lexer import Lexer
from lib.prsr import Parser
from lib.interpreter import Interpreter
from lib.basic.context import Context
from lib.basic.symbol_table import SymbolTable
from lib.number_val import Number
from lib.builtin_func_val import BuildInFunction

global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number.null(), protected=True)
global_symbol_table.set("TRUE", Number.true(), protected=True)
global_symbol_table.set("FALSE", Number.false(), protected=True)
global_symbol_table.set("PI", Number.pi(), protected=True)
global_symbol_table.set("PRINT", BuildInFunction.print(), protected=True)
global_symbol_table.set("PRINT_RET", BuildInFunction.print_ret(), protected=True)
global_symbol_table.set("INPUT", BuildInFunction.input(), protected=True)
global_symbol_table.set("INPUT_NUM", BuildInFunction.input_number(), protected=True)
global_symbol_table.set("CLEAR", BuildInFunction.clear(), protected=True)
global_symbol_table.set("CLS", BuildInFunction.clear(), protected=True)
global_symbol_table.set("IS_NUM", BuildInFunction.is_number(), protected=True)
global_symbol_table.set("IS_STR", BuildInFunction.is_string(), protected=True)
global_symbol_table.set("IS_LIST", BuildInFunction.is_list(), protected=True)
global_symbol_table.set("IS_FUNC", BuildInFunction.is_function(), protected=True)
global_symbol_table.set("IS_INT", BuildInFunction.is_int(), protected=True)
global_symbol_table.set("APPEND", BuildInFunction.append(), protected=True)
global_symbol_table.set("POP", BuildInFunction.pop(), protected=True)
global_symbol_table.set("EXTEND", BuildInFunction.extend(), protected=True)

def run(fn, text):
  if text.strip() == "":
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