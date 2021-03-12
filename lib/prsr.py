from typing import Union, Callable, Iterable
from .basic.error.error import InvalidSyntaxError, ErrorBase
from .nodes import NumberNode, BinOpNode, UnaryOpNode, VarAssignNode, VarAccessNode, IfNode, ForNode, WhileNode, FuncDefNode, CallNode, StringNode, Node
from . import tokenClass

class ParserResult:
  def __init__(self):
    self.error = None
    self.node = None
    self.advance_count = 0

  def register_advancement(self):
    self.advance_count += 1

  def register(self, res):
    self.advance_count += res.advance_count
    if res.error: self.error = res.error
    return res.node

  def success(self, node:Node):
    self.node = node
    return self

  def failure(self, error:ErrorBase):
    if not self.error or self.advance_count == 0:
      self.error = error
    return self

class Parser:
  def __init__(self, tokens : Union[list, dict]):
    self.tokens = tokens
    self.current_token : Union[tokenClass.Token, None] = None
    self.tok_index = -1
    self.advance()

  def advance(self):
    self.tok_index += 1
    if self.tok_index < len(self.tokens):
      self.current_token = self.tokens[self.tok_index]
    return self.current_token

  def parse(self):
    res = self.expr()
    if not res.error and self.current_token.type != tokenClass.TT_EOF:
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '+', '-', '*', '/', '^', '==', '!=', '<', '>', <=', '>=', 'AND' or 'OR'"))
    return res

  def if_expr(self):
    res = ParserResult()
    cases = []
    else_case = None

    if not self.current_token.matches(tokenClass.TT_KEYWORD, "IF"):
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'IF'"))

    res.register_advancement()
    self.advance()

    condition = res.register(self.expr())
    if res.error: return res

    if (not self.current_token.matches(tokenClass.TT_KEYWORD, "THEN")) and (not self.current_token.matches(tokenClass.TT_KEYWORD, ":")):
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'THEN' or ':' (same meaning)"))

    res.register_advancement()
    self.advance()

    expr = res.register(self.expr())
    if res.error: return res

    cases.append((condition, expr))

    while self.current_token.matches(tokenClass.TT_KEYWORD, "ELIF"):
      res.register_advancement()
      self.advance()

      condition = res.register(self.expr())
      if res.error: return res

      if (not self.current_token.matches(tokenClass.TT_KEYWORD, "THEN")) and (not self.current_token.matches(tokenClass.TT_KEYWORD, ":")):
        return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'THEN' or ':' (same meaning)"))

      res.register_advancement()
      self.advance()

      expr = res.register(self.expr())
      if res.error: return res

      cases.append((condition, expr))

    if self.current_token.matches(tokenClass.TT_KEYWORD, "ELSE"):
      res.register_advancement()
      self.advance()

      else_case = res.register(self.expr())
      if res.error: return res

    return res.success(IfNode(cases, else_case))

  def for_expr(self):
    res = ParserResult()

    if not self.current_token.matches(tokenClass.TT_KEYWORD, "FOR"):
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'FOR'"))

    res.register_advancement()
    self.advance()

    if self.current_token.matches(tokenClass.TT_KEYWORD, "VAR"):
      res.register_advancement()
      self.advance()

    if self.current_token.type != tokenClass.TT_IDENTIFIER:
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected identifier or VAR"))

    var_name = self.current_token

    res.register_advancement()
    self.advance()

    if self.current_token.type != tokenClass.TT_EQ:
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '='"))

    res.register_advancement()
    self.advance()

    start_value = res.register(self.expr())
    if res.error: return res

    if not self.current_token.matches(tokenClass.TT_KEYWORD, "TO"):
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'TO'"))

    res.register_advancement()
    self.advance()

    end_value = res.register(self.expr())
    if res.error: return res

    step_value = None
    if self.current_token.matches(tokenClass.TT_KEYWORD, "STEP"):
      res.register_advancement()
      self.advance()

      step_value = res.register(self.expr())
      if res.error: return res

    if (not self.current_token.matches(tokenClass.TT_KEYWORD, "DO")) and (not self.current_token.matches(tokenClass.TT_KEYWORD, ":")):
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'DO' or ':' (same meaning)"))

    res.register_advancement()
    self.advance()

    body = res.register(self.expr())
    if res.error: return res

    return res.success(ForNode(var_name, start_value, end_value, body, step_value))

  def while_expr(self):
    res = ParserResult()

    if not self.current_token.matches(tokenClass.TT_KEYWORD, "WHILE"):
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'WHILE'"))

    res.register_advancement()
    self.advance()

    condition = res.register(self.expr())
    if res.error: return res

    if (not self.current_token.matches(tokenClass.TT_KEYWORD, "DO")) and (not self.current_token.matches(tokenClass.TT_KEYWORD, ":")):
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'DO' or ':' (same meaning)"))

    res.register_advancement()
    self.advance()

    body = res.register(self.expr())
    if res.error: return res

    return res.success(WhileNode(condition, body))

  def power(self):
    return self.bin_op(self.call, (tokenClass.TT_POW,), self.factor)

  def call(self):
    res = ParserResult()
    atom = res.register(self.atom())
    if res.error: return res

    if self.current_token.type == tokenClass.TT_LPAREN:
      res.register_advancement()
      self.advance()

      arg_nodes = []

      if self.current_token == tokenClass.TT_RPAREN:
        res.register_advancement()
        self.advance()
      else:
        arg_nodes.append(res.register(self.expr()))
        if res.error:
          return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'VAR', 'IF', 'WHILE', 'FUNC', int, float, indentifier, '+', '-', '(', ')' or 'NOT'"))

        while self.current_token.type == tokenClass.TT_COMMA:
          res.register_advancement()
          self.advance()
          
          arg_nodes.append(res.register(self.expr()))
          if res.error: return res

        if self.current_token.type != tokenClass.TT_RPAREN:
          return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected ',' or ')'"))

        res.register_advancement()
        self.advance()
      return res.success(CallNode(atom, arg_nodes))
    return res.success(atom)

  def atom(self):
    res = ParserResult()
    tok = self.current_token

    if tok.type in (tokenClass.TT_FLOAT, tokenClass.TT_INT):
      res.register_advancement()
      self.advance()
      return res.success(NumberNode(tok))

    elif tok.type == tokenClass.TT_STRING:
      res.register_advancement()
      self.advance()
      return res.success(StringNode(tok))

    elif tok.type == tokenClass.TT_IDENTIFIER:
      res.register_advancement()
      self.advance()

      return res.success(VarAccessNode(tok))

    elif tok.type == tokenClass.TT_LPAREN:
      res.register_advancement()
      self.advance()
      expr = res.register(self.expr())
      if res.error: return res
      if self.current_token.type == tokenClass.TT_RPAREN:
        res.register_advancement()
        self.advance()
        return res.success(expr)
      else:
        return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected ')'"))

    elif tok.matches(tokenClass.TT_KEYWORD, "IF"):
      if_expr = res.register(self.if_expr())
      if res.error: return res
      return res.success(if_expr)

    elif tok.matches(tokenClass.TT_KEYWORD, "FOR"):
      for_expr = res.register(self.for_expr())
      if res.error: return res
      return res.success(for_expr)

    elif tok.matches(tokenClass.TT_KEYWORD, "WHILE"):
      while_expr = res.register(self.while_expr())
      if res.error: return res
      return res.success(while_expr)

    elif tok.matches(tokenClass.TT_KEYWORD, "FUNC"):
      func_def = res.register(self.func_def())
      if res.error: return res
      return res.success(func_def)

    return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, "Expected int, float, identifier, '+', '-', '(', 'IF', 'FOR', 'WHILE', 'FUN'"))

  def factor(self):
    res = ParserResult()
    tok = self.current_token

    if tok.type in (tokenClass.TT_PLUS, tokenClass.TT_MINUS):
      res.register_advancement()
      self.advance()
      factor = res.register(self.factor())
      if res.error: return res
      return res.success(UnaryOpNode(tok, factor))

    return self.power()

  def term(self):
    return self.bin_op(self.factor, (tokenClass.TT_MUL, tokenClass.TT_DIV))

  def arith_expr(self):
    return self.bin_op(self.term, (tokenClass.TT_PLUS, tokenClass.TT_MINUS))

  def comp_expr(self):
    res = ParserResult()

    if self.current_token.matches(tokenClass.TT_KEYWORD, "NOT"):
      op_tok = self.current_token

      res.register_advancement()
      self.advance()

      node = res.register(self.comp_expr())
      if res.error: return res

      return res.success(UnaryOpNode(op_tok, node))

    node = res.register(self.bin_op(self.arith_expr, (tokenClass.TT_EE, tokenClass.TT_NE, tokenClass.TT_LT, tokenClass.TT_GT, tokenClass.TT_LTE, tokenClass.TT_GTE)))
    if res.error:
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected int, float, identifier, '+', '-', '(' or 'NOT'"))

    return res.success(node)

  def expr(self):
    res = ParserResult()

    if self.current_token.matches(tokenClass.TT_KEYWORD, "VAR"):
      res.register_advancement()
      self.advance()

      if self.current_token.type != tokenClass.TT_IDENTIFIER:
        return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected identifier"))

      var_name = self.current_token
      res.register_advancement()
      self.advance()

      if self.current_token.type == tokenClass.TT_EQ:
        res.register_advancement()
        self.advance()

        expr = res.register(self.expr())
        if res.error: return res

        return res.success(VarAssignNode(var_name, expr))

      return res.success(VarAssignNode(var_name, NumberNode(tokenClass.Token(tokenClass.TT_INT, 0, self.current_token.pos_start, self.current_token.pos_end))))

    node = res.register(self.bin_op(self.comp_expr, ((tokenClass.TT_KEYWORD, "AND"), (tokenClass.TT_KEYWORD, "OR"))))

    if res.error:
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(' or 'NOT'"))

    return res.success(node)

  def bin_op(self, func_a:Callable, ops:Iterable, func_b:Union[Callable, None]=None):
    if func_b is None:
      func_b = func_a

    res = ParserResult()
    left = res.register(func_a())
    if res.error: return res

    while self.current_token.type in ops or (self.current_token.type, self.current_token.value) in ops:
      op_tok = self.current_token
      res.register_advancement()
      self.advance()
      right = res.register(func_b())
      if res.error: return res
      left = BinOpNode(left, op_tok, right)

    return res.success(left)

  def func_def(self):
    res = ParserResult()

    if not self.current_token.matches(tokenClass.TT_KEYWORD, "FUNC"):
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'FUNC'"))

    res.register_advancement()
    self.advance()

    if self.current_token.type == tokenClass.TT_IDENTIFIER:
      var_name_tok = self.current_token

      res.register_advancement()
      self.advance()

      if self.current_token.type != tokenClass.TT_LPAREN:
        return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '('"))
    else:
      var_name_tok = None
      if self.current_token.type != tokenClass.TT_LPAREN:
        return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected identifier or '('"))

    res.register_advancement()
    self.advance()

    arg_name_toks = []
    if self.current_token.type == tokenClass.TT_IDENTIFIER:
      arg_name_toks.append(self.current_token)
      res.register_advancement()
      self.advance()

      while self.current_token.type == tokenClass.TT_COMMA:
        res.register_advancement()
        self.advance()

        if self.current_token.type != tokenClass.TT_IDENTIFIER:
          return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected identifier"))

        arg_name_toks.append(self.current_token)
        res.register_advancement()
        self.advance()

      if self.current_token.type != tokenClass.TT_RPAREN:
        return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected ',' or ')'"))
    else:
      if self.current_token.type != tokenClass.TT_RPAREN:
        return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected identifier or ')'"))

    res.register_advancement()
    self.advance()

    if self.current_token.type != tokenClass.TT_ARROW:
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '->'"))

    res.register_advancement()
    self.advance()

    node_to_return = res.register(self.expr())
    if res.error: return res
      
    return res.success(FuncDefNode(var_name_tok, arg_name_toks, node_to_return))