from basic.error import IllegalCharError, ExpectedCharacterError, ErrorBase
from basic.position import Position
from basic import tokenClass
from typing import Union

class Lexer:
  def __init__(self, fn, text):
    self.fn = fn
    self.text = text
    self.pos = Position(-1, 0, -1, fn, text)
    self.current_char = None
    self.advance()

  def advance(self):
    self.pos.advance(self.current_char)
    self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

  def make_tokens(self)->(list, Union[ErrorBase, None]):
    tokens = []

    while self.current_char is not None:
      if self.current_char in ' \t':
        self.advance()
      elif self.current_char in tokenClass.DIGITS:
        tokens.append(self.make_number())
      elif self.current_char in tokenClass.LATTERS_EXTENDED:
        tokens.append(self.make_identifier())
      elif self.current_char == '+':
        tokens.append(tokenClass.Token(tokenClass.TT_PLUS, pos_start=self.pos))
        self.advance()
      elif self.current_char == '-':
        tokens.append(tokenClass.Token(tokenClass.TT_MINUS, pos_start=self.pos))
        self.advance()
      elif self.current_char == '*':
        tokens.append(tokenClass.Token(tokenClass.TT_MUL, pos_start=self.pos))
        self.advance()
      elif self.current_char == '/':
        tokens.append(tokenClass.Token(tokenClass.TT_DIV, pos_start=self.pos))
        self.advance()
      elif self.current_char == '^':
        tokens.append(tokenClass.Token(tokenClass.TT_POW, pos_start=self.pos))
        self.advance()
      elif self.current_char == '(':
        tokens.append(tokenClass.Token(tokenClass.TT_LPAREN, pos_start=self.pos))
        self.advance()
      elif self.current_char == ')':
        tokens.append(tokenClass.Token(tokenClass.TT_RPAREN, pos_start=self.pos))
        self.advance()
      elif self.current_char == '=':
        tokens.append(self.make_equals())
      elif self.current_char == "!":
        tok, error = self.make_not_equals()
        if error: return [], error
        tokens.append(tok)
      elif self.current_char == '<':
        tokens.append(self.make_less_than())
      elif self.current_char == '>':
        tokens.append(self.make_greater_than())
      elif self.current_char == ":": # Equal to THEN
        tokens.append(tokenClass.Token(tokenClass.TT_KEYWORD, ":", self.pos))
        self.advance()
      else:
        pos_start = self.pos.copy()
        char = self.current_char
        self.advance()
        return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

    tokens.append(tokenClass.Token(tokenClass.TT_EOF, pos_start=self.pos))
    return tokens, None

  def make_number(self):
    num_str = ''
    dot_count = 0
    pos_start = self.pos.copy()

    while self.current_char is not None and self.current_char in tokenClass.DIGITS + '.':
      if self.current_char == '.':
        if dot_count == 1: break
        dot_count += 1
        num_str += '.'
      else:
        num_str += self.current_char
      self.advance()

    if dot_count == 0:
      return tokenClass.Token(tokenClass.TT_INT, int(num_str), pos_start, self.pos)
    else:
      return tokenClass.Token(tokenClass.TT_FLOAT, float(num_str), pos_start, self.pos)

  def make_identifier(self):
    id_string = ""
    pos_start = self.pos.copy()

    while self.current_char is not None and self.current_char in tokenClass.LATTERS_EXTENDED_DIGITS:
      id_string += self.current_char
      self.advance()

    tok_type = tokenClass.TT_KEYWORD if id_string in tokenClass.KEYWORDS else tokenClass.TT_IDENTIFIER
    return tokenClass.Token(tok_type, id_string, pos_start, self.pos)

  def make_not_equals(self):
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == "=":
      self.advance()
      return tokenClass.Token(tokenClass.TT_NE, pos_start=pos_start, pos_end=self.pos), None

    self.advance()
    return None, ExpectedCharacterError(pos_start, self.pos, "'=' (after '!')")

  def make_equals(self):
    token_type = tokenClass.TT_EQ
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == "=":
      self.advance()
      token_type = tokenClass.TT_EE

    return tokenClass.Token(token_type, pos_start=pos_start, pos_end=self.pos)

  def make_less_than(self):
    token_type = tokenClass.TT_LT
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == "=":
      self.advance()
      token_type = tokenClass.TT_LTE

    return tokenClass.Token(token_type, pos_start=pos_start, pos_end=self.pos)

  def make_greater_than(self):
    token_type = tokenClass.TT_GT
    pos_start = self.pos.copy()
    self.advance()

    if self.current_char == "=":
      self.advance()
      token_type = tokenClass.TT_GTE

    return tokenClass.Token(token_type, pos_start=pos_start, pos_end=self.pos)