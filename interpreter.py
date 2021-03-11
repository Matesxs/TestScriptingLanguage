from basic.nodes import Node, BinOpNode, NumberNode, UnaryOpNode, VarAccessNode, VarAssignNode
from basic.number import Number
from basic.error import ErrorBase, RTError
from typing import Union
from basic import tokenClass
from basic.context import Context

class RTResult:
  def __init__(self):
    self.value = None
    self.error:Union[None, ErrorBase] = None

  def register(self, res):
    if res.error: self.error = res.error
    return res.value

  def success(self, value):
    self.value = value
    return self

  def failure(self, error:ErrorBase):
    self.error = error
    return self

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

    value = value.copy().set_position(node.pos_start, node.pos_end)
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