from basic.tokenClass import Token
from typing import Union

class Node:
  def __init__(self):
    self.pos_start = None
    self.pos_end = None

class NumberNode(Node):
  def __init__(self, tok:Token):
    super(NumberNode, self).__init__()
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
  def __init__(self, cases:list, else_case:Node):
    super(IfNode, self).__init__()
    self.cases = cases
    self.else_case = else_case

    self.pos_start = self.cases[0][0].pos_start
    self.pos_end = self.cases[-1][0].pos_end if not self.else_case else else_case.pos_end
  
class ForNode(Node):
  def __init__(self, var_name_token:Token, start_value_node:Node, end_value_node:Node, body_node:Node, step_value_node:Union[Node, None]=None):
    super(ForNode, self).__init__()
    self.var_name_token = var_name_token
    self.start_value_node = start_value_node
    self.end_value_node = end_value_node
    self.body_node = body_node
    self.step_value_node = step_value_node

    self.pos_start = self.var_name_token.pos_start
    self.pos_end = self.body_node.pos_end

class WhileNode(Node):
  def __init__(self, condition_node:Node, body_node:Node):
    super(WhileNode, self).__init__()
    self.condition_node = condition_node
    self.body_node = body_node

    self.pos_start = self.condition_node.pos_start
    self.pos_end = self.body_node.pos_end