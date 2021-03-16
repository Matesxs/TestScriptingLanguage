from typing import Union
import string
from .basic.position import Position

TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"
TT_STRING = "STRING"
TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_POW = "POW"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_LSBRAC = "LSBRAC"
TT_RSBRAC = "RSBRAC"
TT_EQ = "EQ"
TT_EE = "EE"
TT_NE = "NE"
TT_LT = "LT"
TT_GT = "GT"
TT_LTE = "LTE"
TT_GTE = "GTE"
TT_COMMA = "COMMA"
TT_ARROW = "ARROW"
TT_EOF = "EOF"
TT_NEWLINE = "NEWLINE"

DIGITS = "0123456789"
LATTERS = string.ascii_letters
LATTERS_EXTENDED = LATTERS + "_"
LATTERS_DIGITS = LATTERS_EXTENDED + DIGITS
LATTERS_EXTENDED_DIGITS = LATTERS_EXTENDED + DIGITS

ESCAPE_CHARACTERS = {
  "n": "\n",
  "t": "\t"
}

KEYWORDS = [
  "VAR",
  "AND",
  "OR",
  "NOT",
  "IF",
  "ELIF",
  "ELSE",
  "FOR",
  "TO",
  "STEP",
  "WHILE",
  "THEN",
  "FUNC",
  "END",
  "RETURN",
  "CONTINUE",
  "BREAK"
]

class Token:
  def __init__(self, type_, value=None, pos_start:Union[None, Position]=None, pos_end:Union[None, Position]=None):
    self.type = type_
    self.value = value

    if pos_start:
      self.pos_start = pos_start.copy()
      self.pos_end = self.pos_start.copy()
      self.pos_end.advance()

    if pos_end:
      self.pos_end = pos_end.copy()

  def matches(self, type_, value):
    return self.type == type_ and self.value == value

  def __repr__(self):
    if self.value: return f"{self.type}:{self.value}"
    return f"{self.type}"