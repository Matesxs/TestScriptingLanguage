from typing import Union
from .tokenClass import Token
from .basic.position import Position

class Node:
  def __init__(self):
    self.pos_start:Union[Position, None] = None
    self.pos_end:Union[Position, None] = None

class NumberNode(Node):
  def __init__(self, tok:Token):
    super(NumberNode, self).__init__()
    self.tok = tok

    self.pos_start = self.tok.pos_start
    self.pos_end = self.tok.pos_end

class StringNode(Node):
  def __init__(self, tok:Token):
    super(StringNode, self).__init__()
    self.tok = tok

    self.pos_start = self.tok.pos_start
    self.pos_end = self.tok.pos_end

class VarAccessNode(Node):
  def __init__(self, var_name_tok:Token):
    super(VarAccessNode, self).__init__()
    self.var_name_tok = var_name_tok

    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.var_name_tok.pos_end
  
class VarAssignNode(Node):
  def __init__(self, var_name_tok:Token, value_node:Node):
    super(VarAssignNode, self).__init__()
    self.var_name_tok = var_name_tok
    self.value_node = value_node

    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.value_node.pos_end
  
class BinOpNode(Node):
  def __init__(self, left_node:Node, op_tok:Token, right_node:Node):
    super(BinOpNode, self).__init__()
    self.left_node = left_node
    self.op_tok = op_tok
    self.right_node = right_node

    self.pos_start = self.left_node.pos_start
    self.pos_end = self.right_node.pos_end

class UnaryOpNode(Node):
  def __init__(self, op_tok:Token, node:Node):
    super(UnaryOpNode, self).__init__()
    self.op_tok = op_tok
    self.node = node

    self.pos_start = self.op_tok.pos_start
    self.pos_end = node.pos_end
  
class IfNode(Node):
  def __init__(self, cases:list, else_case:tuple):
    super(IfNode, self).__init__()
    self.cases = cases
    self.else_case = else_case

    self.pos_start = self.cases[0][0].pos_start
    self.pos_end = self.cases[-1][0].pos_end if not self.else_case else else_case[0].pos_end
  
class ForNode(Node):
  def __init__(self, var_name_token:Token, start_value_node:Node, end_value_node:Node, body_node:Node, step_value_node:Union[Node, None], should_return_null:bool):
    super(ForNode, self).__init__()
    self.var_name_token = var_name_token
    self.start_value_node = start_value_node
    self.end_value_node = end_value_node
    self.body_node = body_node
    self.step_value_node = step_value_node
    self.should_return_null = should_return_null

    self.pos_start = self.var_name_token.pos_start
    self.pos_end = self.body_node.pos_end

class WhileNode(Node):
  def __init__(self, condition_node:Node, body_node:Node, should_return_null:bool):
    super(WhileNode, self).__init__()
    self.condition_node = condition_node
    self.body_node = body_node
    self.should_return_null = should_return_null

    self.pos_start = self.condition_node.pos_start
    self.pos_end = self.body_node.pos_end

class FuncDefNode(Node):
  def __init__(self, var_name_tok:Union[Token, None], arg_name_toks:list, body_node:Node, should_auto_return:bool):
    super(FuncDefNode, self).__init__()
    self.var_name_tok = var_name_tok
    self.arg_name_toks = arg_name_toks
    self.body_node = body_node
    self.should_auto_return = should_auto_return

    if self.var_name_tok:
      self.pos_start = self.var_name_tok.pos_start
    elif len(arg_name_toks) > 0:
      self.pos_start = self.arg_name_toks[0].pos_start
    else:
      self.pos_start = self.body_node.pos_start

    self.pos_end = self.body_node.pos_end

class CallNode(Node):
  def __init__(self, node_to_call:Node, arg_nodes:list):
    super(CallNode, self).__init__()
    self.node_to_call = node_to_call
    self.arg_nodes = arg_nodes

    self.pos_start = node_to_call.pos_start
    if len(self.arg_nodes) > 0:
      self.pos_end = self.arg_nodes[-1].pos_end
    else:
      self.pos_end = self.node_to_call.pos_end

class ListNode(Node):
  def __init__(self, element_nodes:list, pos_start:Union[Position, None]=None, pos_end:Union[Position, None]=None):
    super(ListNode, self).__init__()
    self.element_nodes = element_nodes

    self.pos_start = pos_start
    self.pos_end = pos_end

class ReturnNode(Node):
  def __init__(self, node_to_return:Union[Node, None], pos_start:Union[Position, None]=None, pos_end:Union[Position, None]=None):
    super(ReturnNode, self).__init__()
    self.node_to_return = node_to_return

    self.pos_start = pos_start
    self.pos_end = pos_end

class ContinueNode(Node):
  def __init__(self, pos_start:Union[Position, None]=None, pos_end:Union[Position, None]=None):
    super(ContinueNode, self).__init__()
    self.pos_start = pos_start
    self.pos_end = pos_end

class BreakNode(Node):
  def __init__(self, pos_start:Union[Position, None]=None, pos_end:Union[Position, None]=None):
    super(BreakNode, self).__init__()
    self.pos_start = pos_start
    self.pos_end = pos_end
