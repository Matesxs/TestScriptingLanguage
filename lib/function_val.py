from typing import Union
from .nodes import Node
from .basic.error import RTError
from . import Value
from . import RTResult
from . import Context
from . import SymbolTable

class Function(Value):
  def __init__(self, name:Union[str, None], body_node:Node, arg_names:list):
    super(Function, self).__init__()
    self.name = name or "<anonymous>"
    self.body_node = body_node
    self.arg_names = arg_names

  def execute(self, args, interpreter):
    res = RTResult()

    new_context = Context(self.name, self.context, self.pos_start)
    new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)

    if len(args) > len(self.arg_names):
      return res.failure(RTError(self.pos_start, self.pos_end, f"{len(args) - len(self.arg_names)} too many arguments passed to '{self.name}' function", self.context))
    elif len(args) < len(self.arg_names):
      return res.failure(RTError(self.pos_start, self.pos_end, f"{len(self.arg_names) - len(args)} too few arguments passed to '{self.name}' function", self.context))

    for i in range(len(args)):
      arg_name = self.arg_names[i]
      arg_value = args[i]
      arg_value.set_context(new_context)
      new_context.symbol_table.set(arg_name, arg_value)

    value = res.register(interpreter.visit(self.body_node, new_context))
    if res.error: return res
    return res.success(value)

  def copy(self):
    copy = Function(self.name, self.body_node, self.arg_names)
    copy.set_context(self.context)
    copy.set_position(self.pos_start, self.pos_end)
    return copy

  def __repr__(self):
    return f"<function {self.name}>"