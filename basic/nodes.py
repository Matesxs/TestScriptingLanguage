from basic.tokenClass import Token

class Node:
  def __init__(self):
    self.pos_start = None
    self.pos_end = None

  def __repr__(self):
    raise NotImplementedError("To be implemented")

class NumberNode(Node):
  def __init__(self, tok:Token):
    super(NumberNode, self).__init__()
    self.tok = tok

    self.pos_start = self.tok.pos_start
    self.pos_end = self.tok.pos_end

  def __repr__(self):
    return f"{self.tok}"

class VarAccessNode(Node):
  def __init__(self, var_name_tok:Token):
    super(VarAccessNode, self).__init__()
    self.var_name_tok = var_name_tok

    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.var_name_tok.pos_end

  def __repr__(self):
    return f"({self.var_name_tok})"
  
class VarAssignNode(Node):
  def __init__(self, var_name_tok:Token, value_node:Node):
    super(VarAssignNode, self).__init__()
    self.var_name_tok = var_name_tok
    self.value_node = value_node

    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.value_node.pos_end

  def __repr__(self):
    return f"({self.var_name_tok} = {self.value_node})"
  
class BinOpNode(Node):
  def __init__(self, left_node:Node, op_tok:Token, right_node:Node):
    super(BinOpNode, self).__init__()
    self.left_node = left_node
    self.op_tok = op_tok
    self.right_node = right_node

    self.pos_start = self.left_node.pos_start
    self.pos_end = self.right_node.pos_end

  def __repr__(self):
    return f"({self.left_node}, {self.op_tok}, {self.right_node})"

class UnaryOpNode(Node):
  def __init__(self, op_tok:Token, node:Node):
    super(UnaryOpNode, self).__init__()
    self.op_tok = op_tok
    self.node = node

    self.pos_start = self.op_tok.pos_start
    self.pos_end = node.pos_end

  def __repr__(self):
    return f"({self.op_tok}, {self.node})"