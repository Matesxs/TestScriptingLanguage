import os
import subprocess
from typing import Union
from .basic.base_function import BaseFunction
from .basic.runtime_result import RTResult
from .basic.context import Context
from .basic.error import RTError
from .number_val import Number
from .string_val import String
from .list_val import List

class BuildInFunction(BaseFunction):
  def __init__(self, name: Union[str, None]):
    super(BuildInFunction, self).__init__(name)

  def execute(self, args: list, interpreter) -> RTResult:
    res = RTResult()

    exec_ctx = self.generate_new_context()

    method_name = f"execute_{self.name}"
    method = getattr(self, method_name, self.no_execute_method)

    res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
    if res.should_return(): return res

    return_value = res.register(method(exec_ctx))
    if res.should_return(): return res

    return res.success(return_value)

  def no_execute_method(self, node, context):
    raise Exception(f"No execute_{self.name} method defined")

  def copy(self):
    return BuildInFunction(self.name).set_context(self.context).set_position(self.pos_start, self.pos_end)

  def __repr__(self):
    return f"<built-in function {self.name}>"

  def execute_print(self, exec_context: Context) -> RTResult:
    print(str(exec_context.symbol_table.get("value")))
    return RTResult().success(Number.null())

  execute_print.arg_names = ["value"]

  def execute_print_ret(self, exec_context: Context) -> RTResult:
    return RTResult().success(String(str(exec_context.symbol_table.get("value"))))

  execute_print_ret.arg_names = ["value"]

  def execute_input(self, _) -> RTResult:
    return RTResult().success(String(input()))

  execute_input.arg_names = []

  def execute_input_number(self, exec_context: Context) -> RTResult:
    inp = input()

    try:
      number = int(inp)
    except ValueError:
      try:
        number = float(inp)
      except ValueError:
        return RTResult().failure(RTError(self.pos_start, self.pos_end, "Argument must be int or float convertable", exec_context))

    return RTResult().success(Number(number))

  execute_input_number.arg_names = []

  def execute_clear(self, _) -> RTResult:
    os.system("cls" if os.name == "nt" else "clear")
    return RTResult().success(Number.null())

  execute_clear.arg_names = []

  def execute_is_number(self, exec_context: Context) -> RTResult:
    is_number = isinstance(exec_context.symbol_table.get("value"), Number)
    return RTResult().success(Number.true() if is_number else Number.false())

  execute_is_number.arg_names = ["value"]

  def execute_is_int(self, exec_context: Context) -> RTResult:
    val = exec_context.symbol_table.get("value")
    if not isinstance(val, Number):
      return RTResult().success(Number.false())

    return RTResult().success(Number.true() if val.value == int(val.value) else Number.false())
  execute_is_int.arg_names = ["value"]

  def execute_is_string(self, exec_context: Context) -> RTResult:
    is_string = isinstance(exec_context.symbol_table.get("value"), String)
    return RTResult().success(Number.true() if is_string else Number.false())

  execute_is_string.arg_names = ["value"]

  def execute_is_list(self, exec_context: Context) -> RTResult:
    is_list = isinstance(exec_context.symbol_table.get("value"), List)
    return RTResult().success(Number.true() if is_list else Number.false())

  execute_is_list.arg_names = ["value"]

  def execute_is_function(self, exec_context: Context) -> RTResult:
    is_function = isinstance(exec_context.symbol_table.get("value"), BaseFunction)
    return RTResult().success(Number.true() if is_function else Number.false())

  execute_is_function.arg_names = ["value"]

  def execute_append(self, exec_context: Context) -> RTResult:
    list_ = exec_context.symbol_table.get("list")
    value = exec_context.symbol_table.get("value")

    if not isinstance(list_, List):
      return RTResult().failure(RTError(self.pos_start, self.pos_end, "First argument must be list", exec_context))

    list_.elements.append(value)
    return RTResult().success(Number.null())

  execute_append.arg_names = ["list", "value"]

  def execute_pop(self, exec_context: Context) -> RTResult:
    list_ = exec_context.symbol_table.get("list")
    index = exec_context.symbol_table.get("index")

    if not isinstance(list_, List):
      return RTResult().failure(RTError(self.pos_start, self.pos_end, "First argument must be list", exec_context))

    if not isinstance(index, Number):
      return RTResult().failure(RTError(self.pos_start, self.pos_end, "Second argument must be number", exec_context))

    try:
      element = list_.elements.pop(index.value)
    except:
      return RTResult().failure(RTError(self.pos_start, self.pos_end, "Element of that index could not be removed because that index doesn't exist", exec_context))

    return RTResult().success(element)

  execute_pop.arg_names = ["list", "index"]

  def execute_extend(self, exec_context: Context) -> RTResult:
    listA = exec_context.symbol_table.get("listA")
    listB = exec_context.symbol_table.get("listB")

    if not isinstance(listA, List):
      return RTResult().failure(RTError(self.pos_start, self.pos_end, "First argument must be list", exec_context))

    if not isinstance(listB, List):
      return RTResult().failure(RTError(self.pos_start, self.pos_end, "Second argument must be list", exec_context))

    listA.elements.extend(listB.elements)
    return RTResult().success(Number.null())

  execute_extend.arg_names = ["listA", "listB"]

  def execute_len(self, exec_context: Context) -> RTResult:
    _list = exec_context.symbol_table.get("list")
    
    if not isinstance(_list, List):
      return RTResult().failure(RTError(self.pos_start, self.pos_end, "Argument must be list", exec_context))

    return RTResult().success(Number(len(_list.elements)))
  execute_len.arg_names = ["list"]

  def execute_run(self, exec_context: Context) -> RTResult:
    fn = exec_context.symbol_table.get("fn")

    if not isinstance(fn, String):
      return RTResult().failure(RTError(self.pos_start, self.pos_end, "Argument must be string", exec_context))

    fn = fn.value

    if not os.path.exists(fn):
      return RTResult().failure(RTError(self.pos_start, self.pos_end, "Path doesn't exist", exec_context))

    if not os.path.isfile(fn):
      return RTResult().failure(RTError(self.pos_start, self.pos_end, "Path is not file", exec_context))

    try:
      process = subprocess.Popen(f"python {exec_context.symbol_table.entry_point} {fn}")
      process.wait()
    except Exception as e:
      return RTResult().failure(RTError(self.pos_start, self.pos_end, f"Failed to execute script \"{fn}\"\n{e}", exec_context))

    return RTResult().success(Number.null())

  execute_run.arg_names = ["fn"]

  @classmethod
  def print(cls):
    return BuildInFunction("print")

  @classmethod
  def print_ret(cls):
    return BuildInFunction("print_ret")

  @classmethod
  def input(cls):
    return BuildInFunction("input")

  @classmethod
  def input_number(cls):
    return BuildInFunction("input_number")

  @classmethod
  def clear(cls):
    return BuildInFunction("clear")

  @classmethod
  def is_number(cls):
    return BuildInFunction("is_number")

  @classmethod
  def is_int(cls):
    return BuildInFunction("is_int")

  @classmethod
  def is_string(cls):
    return BuildInFunction("is_string")

  @classmethod
  def is_list(cls):
    return BuildInFunction("is_list")

  @classmethod
  def is_function(cls):
    return BuildInFunction("is_function")

  @classmethod
  def append(cls):
    return BuildInFunction("append")

  @classmethod
  def pop(cls):
    return BuildInFunction("pop")

  @classmethod
  def extend(cls):
    return BuildInFunction("extend")

  @classmethod
  def len(cls):
    return BuildInFunction("len")

  @classmethod
  def run(cls):
    return BuildInFunction("run")