from typing import Union
from .basic.runtime_result import RTResult
from .basic.base_function import BaseFunction
from .nodes import Node
from .number_val import Number

class Function(BaseFunction):
  def __init__(self, name:Union[str, None], body_node:Node, arg_names:list, should_return_null:bool):
    super(Function, self).__init__(name)
    self.body_node = body_node
    self.arg_names = arg_names
    self.should_return_null = should_return_null

  def execute(self, args:list, interpreter):
    res = RTResult()

    exec_ctx = self.generate_new_context()

    res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
    if res.error: return res

    value = res.register(interpreter.visit(self.body_node, exec_ctx))
    if res.error: return res
    return res.success(Number.null() if self.should_return_null else value)

  def copy(self):
    copy = Function(self.name, self.body_node, self.arg_names, self.should_return_null)
    copy.set_context(self.context)
    copy.set_position(self.pos_start, self.pos_end)
    return copy

  def __repr__(self):
    return f"<function {self.name}>"