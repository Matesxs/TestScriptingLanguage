from typing import Union
from .basic.runtime_result import RTResult
from .basic.base_function import BaseFunction
from .nodes import Node
from .number_val import Number

class Function(BaseFunction):
  def __init__(self, name:Union[str, None], body_node:Node, arg_names:list, should_auto_return:bool):
    super(Function, self).__init__(name)
    self.body_node = body_node
    self.arg_names = arg_names
    self.should_auto_return = should_auto_return

  def execute(self, args:list, interpreter):
    res = RTResult()

    exec_ctx = self.generate_new_context()

    res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
    if res.should_return(): return res

    value = res.register(interpreter.visit(self.body_node, exec_ctx))
    if res.should_return() and res.func_ret_val is None: return res

    ret_val = (value if self.should_auto_return else None) or res.func_ret_val or Number.null()
    return res.success(ret_val)

  def copy(self):
    copy = Function(self.name, self.body_node, self.arg_names, self.should_auto_return)
    copy.set_context(self.context)
    copy.set_position(self.pos_start, self.pos_end)
    return copy

  def __repr__(self):
    return f"<function {self.name}>"