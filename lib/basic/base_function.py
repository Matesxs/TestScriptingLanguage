from typing import Union
from .context import Context
from .value import Value
from .symbol_table import SymbolTable
from .runtime_result import RTResult
from .error import RTError

def populate_args(arg_names:list, args:list, exec_ctx:Context):
  for i in range(len(args)):
    arg_name = arg_names[i]
    arg_value = args[i]
    arg_value.set_context(exec_ctx)
    exec_ctx.symbol_table.set(arg_name, arg_value)

class BaseFunction(Value):
  def __init__(self, name:Union[str, None]):
    super(BaseFunction, self).__init__()
    self.name = name or "<anonymous>"

  def generate_new_context(self) -> Context:
    new_context = Context(self.name, self.context, self.pos_start)
    new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
    return new_context

  def check_args(self, arg_names:list, args:list) -> RTResult:
    res = RTResult()

    if len(args) > len(arg_names):
      return res.failure(RTError(self.pos_start, self.pos_end, f"{len(args) - len(arg_names)} too many arguments passed to '{self.name}' function", self.context))
    elif len(args) < len(arg_names):
      return res.failure(RTError(self.pos_start, self.pos_end, f"{len(arg_names) - len(args)} too few arguments passed to '{self.name}' function", self.context))

    return res.success(None)

  def check_and_populate_args(self, arg_names:list, args:list, exec_ctx:Context) -> RTResult:
    res = RTResult()

    res.register(self.check_args(arg_names, args))
    if res.error: return res

    populate_args(arg_names, args, exec_ctx)
    return res.success(None)

  def __repr__(self):
    raise NotImplementedError("To be implemented by child classes")