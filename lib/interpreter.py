from typing import Union
from .basic.error import ErrorBase, RTError
from .nodes import Node, BinOpNode, NumberNode, UnaryOpNode, VarAccessNode, VarAssignNode, IfNode, ForNode, WhileNode, FuncDefNode, CallNode, StringNode, ListNode
from .basic.context import Context
from .basic.runtime_result import RTResult
from . import tokenClass
from .basic.value import Value
from .function_val import Function
from .number_val import Number
from .string_val import String
from .list_val import List

class Interpreter:
  def visit(self, node:Node, context:Context):
    method_name = f"visit_{type(node).__name__}"
    method = getattr(self, method_name, self.no_visit_method)
    return method(node, context)

  def no_visit_method(self, node:Node, context:Context):
    raise Exception(f"No visit_{type(node).__name__} method defined")

  def visit_VarAccessNode(self, node:VarAccessNode, context:Context) -> RTResult:
    res = RTResult()

    var_name = node.var_name_tok.value
    value = context.symbol_table.get(var_name)

    if not value:
      return res.failure(RTError(node.pos_start, node.pos_end, f"'{var_name}' is not defined", context))

    value = value.copy().set_position(node.pos_start, node.pos_end).set_context(context)
    return res.success(value)

  def visit_VarAssignNode(self, node:VarAssignNode, context:Context) -> RTResult:
    res = RTResult()

    var_name = node.var_name_tok.value
    value = res.register(self.visit(node.value_node, context))
    if res.error: return res

    if not context.symbol_table.set(var_name, value):
      return res.failure(RTError(node.var_name_tok.pos_start, node.var_name_tok.pos_end, "Invalid identifier - Protected variable", context))
    return res.success(value)

  def visit_NumberNode(self, node:NumberNode, context:Context) -> RTResult:
    return RTResult().success(Number(node.tok.value).set_context(context).set_position(node.pos_start, node.pos_end))

  def visit_BinOpNode(self, node:BinOpNode, context:Context) -> RTResult:
    res = RTResult()

    left:Number = res.register(self.visit(node.left_node, context))
    if res.error: return res
    right:Number = res.register(self.visit(node.right_node, context))
    if res.error: return res

    result = Number(0)
    error:Union[None, ErrorBase] = None

    if node.op_tok.type == tokenClass.TT_PLUS:
      result, error = left.added_to(right)
    elif node.op_tok.type == tokenClass.TT_MINUS:
      result, error = left.subbed_by(right)
    elif node.op_tok.type == tokenClass.TT_MUL:
      result, error = left.multed_by(right)
    elif node.op_tok.type == tokenClass.TT_DIV:
      result, error = left.dived_by(right)
    elif node.op_tok.type == tokenClass.TT_POW:
      result, error = left.powed_by(right)
    elif node.op_tok.type == tokenClass.TT_EE:
      result, error = left.get_comparison_eq(right)
    elif node.op_tok.type == tokenClass.TT_NE:
      result, error = left.get_comparison_ne(right)
    elif node.op_tok.type == tokenClass.TT_LT:
      result, error = left.get_comparison_lt(right)
    elif node.op_tok.type == tokenClass.TT_GT:
      result, error = left.get_comparison_gt(right)
    elif node.op_tok.type == tokenClass.TT_LTE:
      result, error = left.get_comparison_lte(right)
    elif node.op_tok.type == tokenClass.TT_GTE:
      result, error = left.get_comparison_gte(right)
    elif node.op_tok.matches(tokenClass.TT_KEYWORD, 'AND'):
      result, error = left.anded_by(right)
    elif node.op_tok.matches(tokenClass.TT_KEYWORD, 'OR'):
      result, error = left.ored_by(right)

    if error: return res.failure(error)
    return res.success(result.set_position(node.pos_start, node.pos_end))

  def visit_UnaryOpNode(self, node:UnaryOpNode, context:Context) -> RTResult:
    res = RTResult()

    number = res.register(self.visit(node.node, context))
    if res.error: return res

    error: Union[None, ErrorBase] = None
    if node.op_tok.type == tokenClass.TT_MINUS:
      number, error = number.multed_by(Number(-1))
    elif node.op_tok.matches(tokenClass.TT_KEYWORD, "NOT"):
      number, error = number.notted()

    if error: return res.failure(error)
    return res.success(number.set_position(node.pos_start, node.pos_end))

  def visit_IfNode(self, node:IfNode, context:Context) -> RTResult:
    res = RTResult()

    for condition, expr in node.cases:
      condition_value = res.register(self.visit(condition, context))
      if res.error: return res

      if condition_value.is_true():
        expr_value = res.register(self.visit(expr, context))
        if res.error: return res
        return res.success(expr_value)

    if node.else_case:
      else_value = res.register(self.visit(node.else_case, context))
      if res.error: return res
      return res.success(else_value)

    return res.success(None)

  def visit_ForNode(self, node:ForNode, context:Context) -> RTResult:
    res = RTResult()
    elements = []

    start_value:Number = res.register(self.visit(node.start_value_node, context))
    if res.error: return res

    end_value:Number = res.register(self.visit(node.end_value_node, context))
    if res.error: return res

    if node.step_value_node:
      step_value:Number = res.register(self.visit(node.step_value_node, context))
      if res.error: return res
    else:
      step_value:Number = Number(1)

    i = start_value.value
    if step_value.value >= 0:
      condition = lambda: i < end_value.value
    else:
      condition = lambda: i > end_value.value

    while condition():
      context.symbol_table.set(node.var_name_token.value, Number(i))
      i += step_value.value
      
      elements.append(res.register(self.visit(node.body_node, context)))
      if res.error: return res

    return res.success(List(elements).set_context(context).set_position(node.pos_start, node.pos_end))

  def visit_WhileNode(self, node:WhileNode, context:Context) -> RTResult:
    res = RTResult()
    elements = []

    condition:Value = res.register(self.visit(node.condition_node, context))
    if res.error: return res

    while condition.is_true():
      elements.append(res.register(self.visit(node.body_node, context)))
      if res.error: return res

      condition:Value = res.register(self.visit(node.condition_node, context))
      if res.error: return res

    return res.success(List(elements).set_context(context).set_position(node.pos_start, node.pos_end))

  def visit_FuncDefNode(self, node:FuncDefNode, context:Context) -> RTResult:
    res = RTResult()

    func_name = node.var_name_tok.value if node.var_name_tok else None
    body_node = node.body_node
    arg_names = [arg_name.value for arg_name in node.arg_name_toks]
    func_value = Function(func_name, body_node, arg_names).set_context(context).set_position(node.pos_start, node.pos_end)

    if node.var_name_tok:
      context.symbol_table.set(func_name, func_value)

    return res.success(func_value)

  def visit_CallNode(self, node:CallNode, context:Context) -> RTResult:
    res = RTResult()
    args = []

    value_to_call = res.register(self.visit(node.node_to_call, context))
    if res.error: return res

    value_to_call:Function = value_to_call.copy().set_position(node.pos_start, node.pos_end)

    for arg_node in node.arg_nodes:
      args.append(res.register(self.visit(arg_node, context)))
      if res.error: return res

    return_val = res.register(value_to_call.execute(args, self))
    if res.error: return res

    return_val = return_val.copy().set_position(node.pos_start, node.pos_end).set_context(context)
    return res.success(return_val)

  def visit_StringNode(self, node:StringNode, context:Context) -> RTResult:
    return RTResult().success(String(node.tok.value).set_position(node.pos_start, node.pos_end).set_context(context))

  def visit_ListNode(self, node:ListNode, context:Context) -> RTResult:
    res = RTResult()
    elements = []

    for element_node in node.element_nodes:
      elements.append(res.register(self.visit(element_node, context)))
      if res.error: return res

    return res.success(List(elements).set_context(context).set_position(node.pos_start, node.pos_end))