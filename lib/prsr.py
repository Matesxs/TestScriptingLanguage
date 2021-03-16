from typing import Union, Callable, Iterable
from .basic.error import InvalidSyntaxError, ErrorBase
from .nodes import Node, NumberNode, BinOpNode, UnaryOpNode, VarAssignNode, VarAccessNode, IfNode, ForNode, WhileNode, FuncDefNode, CallNode, StringNode, ListNode, ReturnNode, ContinueNode, BreakNode
from . import tokenClass

class ParserResult:
  def __init__(self):
    self.error = None
    self.node = None
    self.last_registered_advance_count = 0
    self.advance_count = 0
    self.to_reverse_count = 0

  def register_advancement(self):
    self.last_registered_advance_count = 1
    self.advance_count += 1

  def register(self, res):
    self.last_registered_advance_count = res.advance_count
    self.advance_count += res.advance_count
    if res.error: self.error = res.error
    return res.node

  def try_register(self, res):
    if res.error:
      self.to_reverse_count = res.advance_count
      return None
    return self.register(res)

  def success(self, node:Union[Node, None, tuple]):
    self.node = node
    return self

  def failure(self, error:ErrorBase):
    if not self.error or self.last_registered_advance_count == 0:
      self.error = error
    return self

class Parser:
  def __init__(self, tokens : Union[list, dict]):
    self.tokens = tokens
    self.current_token : Union[tokenClass.Token, None] = None
    self.tok_index = -1
    self.advance()

  def reverse(self, amount:int=1):
    self.tok_index -= amount
    self.update_current_token()
    return self.current_token

  def advance(self):
    self.tok_index += 1
    self.update_current_token()
    return self.current_token

  def update_current_token(self):
    if 0 <= self.tok_index < len(self.tokens):
      self.current_token = self.tokens[self.tok_index]

  def parse(self):
    res = self.statements()
    if not res.error and self.current_token.type != tokenClass.TT_EOF:
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '+', '-', '*', '/', '^', '==', '!=', '<', '>', <=', '>=', 'AND' or 'OR'"))
    return res

  def statements(self):
    res = ParserResult()
    statements = []
    start_pos = self.current_token.pos_start.copy()

    while self.current_token.type == tokenClass.TT_NEWLINE:
      res.register_advancement()
      self.advance()

    statement = res.register(self.statement())
    if res.error: return res
    statements.append(statement)

    more_statements = True

    while True:
      new_line_count = 0
      while self.current_token.type == tokenClass.TT_NEWLINE:
        res.register_advancement()
        self.advance()
        new_line_count += 1

      if new_line_count == 0:
        more_statements = False

      if not more_statements:
        break

      statement = res.try_register(self.statement())
      if not statement:
        self.reverse(res.to_reverse_count)
        more_statements = False
        continue

      statements.append(statement)

    return res.success(ListNode(statements, start_pos, self.current_token.pos_end.copy()))

  def statement(self):
    res = ParserResult()
    pos_start = self.current_token.pos_start.copy()

    if self.current_token.matches(tokenClass.TT_KEYWORD, "RETURN"):
      res.register_advancement()
      self.advance()

      expr = res.try_register(self.expr())
      if not expr:
        self.reverse(res.to_reverse_count)
      return res.success(ReturnNode(expr, pos_start, self.current_token.pos_end.copy()))
    elif self.current_token.matches(tokenClass.TT_KEYWORD, "CONTINUE"):
      res.register_advancement()
      self.advance()
      return res.success(ContinueNode(pos_start, self.current_token.pos_end.copy()))
    elif self.current_token.matches(tokenClass.TT_KEYWORD, "BREAK"):
      res.register_advancement()
      self.advance()
      return res.success(BreakNode(pos_start, self.current_token.pos_end.copy()))
    
    expr = res.register(self.expr())
    if res.error:
      return res.failure(InvalidSyntaxError(pos_start, self.current_token.pos_end, "Expected 'RETURN', 'CONTINUE', 'BREAK' 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[' or 'NOT'"))

    return res.success(expr)

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
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'VAR', 'IF', 'FOR', 'WHILE', 'FUN', int, float, identifier, '+', '-', '(', '[' or 'NOT'"))

    return res.success(node)

  def if_expr(self):
    res = ParserResult()
    all_cases = res.register(self.if_expr_cases("IF"))
    if res.error: return res
    cases, else_case = all_cases
    return res.success(IfNode(cases, else_case))

  def if_expr_b(self):
    return self.if_expr_cases("ELIF")

  def if_expr_c(self):
    res = ParserResult()
    else_case = None

    if self.current_token.matches(tokenClass.TT_KEYWORD, "ELSE"):
      res.register_advancement()
      self.advance()

      if self.current_token.type == tokenClass.TT_NEWLINE:
        res.register_advancement()
        self.advance()

        statements = res.register(self.statements())
        if res.error: return res
        else_case = (statements, True)

        if self.current_token.matches(tokenClass.TT_KEYWORD, "END"):
          res.register_advancement()
          self.advance()
        else:
          return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'END'"))
      else:
        expr = res.register(self.statement())
        if res.error: return res
        else_case = (expr, False)

    return res.success(else_case)

  def if_expr_b_or_c(self):
    res = ParserResult()
    cases, else_case = [], None

    if self.current_token.matches(tokenClass.TT_KEYWORD, "ELIF"):
      all_cases = res.register(self.if_expr_b())
      if res.error: return res
      cases, else_case = all_cases
    else:
      else_case = res.register(self.if_expr_c())
      if res.error: return res
    
    return res.success((cases, else_case))

  def if_expr_cases(self, case_keyword:str):
    res = ParserResult()
    cases = []
    else_case = None

    if not self.current_token.matches(tokenClass.TT_KEYWORD, case_keyword):
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, f"Expected '{case_keyword}'"))

    res.register_advancement()
    self.advance()

    condition = res.register(self.expr())
    if res.error: return res

    if not self.current_token.matches(tokenClass.TT_KEYWORD, "THEN"):
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'THEN'"))

    res.register_advancement()
    self.advance()

    if self.current_token.type == tokenClass.TT_NEWLINE:
      res.register_advancement()
      self.advance()

      statements = res.register(self.statements())
      if res.error: return res
      cases.append((condition, statements, True))

      if self.current_token.matches(tokenClass.TT_KEYWORD, "END"):
        res.register_advancement()
        self.advance()
      else:
        all_cases = res.register(self.if_expr_b_or_c())
        if res.error: return res
        new_cases, else_case = all_cases
        cases.extend(new_cases)
    else:
      expr = res.register(self.statement())
      if res.error: return res
      cases.append((condition, expr, False))

      all_cases = res.register(self.if_expr_b_or_c())
      if res.error: return res
      new_cases, else_case = all_cases
      cases.extend(new_cases)
      
    return res.success((cases, else_case))

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

    if not self.current_token.matches(tokenClass.TT_KEYWORD, "THEN"):
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'THEN'"))

    res.register_advancement()
    self.advance()

    if self.current_token.type == tokenClass.TT_NEWLINE:
      res.register_advancement()
      self.advance()

      body = res.register(self.statements())
      if res.error: return res

      if not self.current_token.matches(tokenClass.TT_KEYWORD, "END"):
        return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'END'"))

      res.register_advancement()
      self.advance()

      return res.success(ForNode(var_name, start_value, end_value, body, step_value, True))

    body = res.register(self.statement())
    if res.error: return res

    return res.success(ForNode(var_name, start_value, end_value, body, step_value, False))

  def while_expr(self):
    res = ParserResult()

    if not self.current_token.matches(tokenClass.TT_KEYWORD, "WHILE"):
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'WHILE'"))

    res.register_advancement()
    self.advance()

    condition = res.register(self.expr())
    if res.error: return res

    if not self.current_token.matches(tokenClass.TT_KEYWORD, "THEN"):
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'THEN'"))

    res.register_advancement()
    self.advance()

    if self.current_token.type == tokenClass.TT_NEWLINE:
      res.register_advancement()
      self.advance()

      body = res.register(self.statements())
      if res.error: return res

      if not self.current_token.matches(tokenClass.TT_KEYWORD, "END"):
        return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'END'"))

      res.register_advancement()
      self.advance()

      return res.success(WhileNode(condition, body, True))

    body = res.register(self.statement())
    if res.error: return res

    return res.success(WhileNode(condition, body, False))

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

      if self.current_token.type == tokenClass.TT_RPAREN:
        res.register_advancement()
        self.advance()
      else:
        arg_nodes.append(res.register(self.expr()))
        if res.error:
          return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'VAR', 'IF', 'WHILE', 'FUNC', int, float, indentifier, '+', '-', '(', ')', '[' or 'NOT'"))

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

    elif tok.type == tokenClass.TT_LSBRAC:
      list_expr = res.register(self.list_expr())
      if res.error: return res
      return res.success(list_expr)

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

    return res.failure(InvalidSyntaxError(tok.pos_start, tok.pos_end, "Expected int, float, identifier, '+', '-', '(', '[', 'IF', 'FOR', 'WHILE', 'FUN'"))

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
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected int, float, identifier, '+', '-', '(', '[' or 'NOT'"))

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

    if self.current_token.type == tokenClass.TT_ARROW:
      res.register_advancement()
      self.advance()

      node_to_return = res.register(self.expr())
      if res.error: return res
      
      return res.success(FuncDefNode(var_name_tok, arg_name_toks, node_to_return, True))

    if self.current_token.type != tokenClass.TT_NEWLINE:
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '->' or NEWLINE"))

    res.register_advancement()
    self.advance()

    body = res.register(self.statements())
    if res.error: return res

    if not self.current_token.matches(tokenClass.TT_KEYWORD, "END"):
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'END'"))

    res.register_advancement()
    self.advance()

    return res.success(FuncDefNode(var_name_tok, arg_name_toks, body, False))

  def list_expr(self):
    res = ParserResult()
    element_nodes = []
    pos_start = self.current_token.pos_start.copy()

    if self.current_token.type != tokenClass.TT_LSBRAC:
      return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected '['"))

    res.register_advancement()
    self.advance()

    if self.current_token.type == tokenClass.TT_RSBRAC:
      res.register_advancement()
      self.advance()
    else:
      element_nodes.append(res.register(self.expr()))
      if res.error:
        return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected 'VAR', 'IF', 'WHILE', 'FUNC', int, float, indentifier, '+', '-', '(', '[', ']' or 'NOT'"))

      while self.current_token.type == tokenClass.TT_COMMA:
        res.register_advancement()
        self.advance()

        element_nodes.append(res.register(self.expr()))
        if res.error: return res

      if self.current_token.type != tokenClass.TT_RSBRAC:
        return res.failure(InvalidSyntaxError(self.current_token.pos_start, self.current_token.pos_end, "Expected ',' or ']'"))

      res.register_advancement()
      self.advance()
      
    return res.success(ListNode(element_nodes, pos_start, self.current_token.pos_end))