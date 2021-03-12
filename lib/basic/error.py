from typing import Union
from termcolor import colored
from .position import Position
from . import Context
from . import string_with_arrows

class ErrorBase:
  def as_string(self):
    raise NotImplementedError("To be implemented")

class Error(ErrorBase):
  def __init__(self, pos_start:Union[None, Position], pos_end:Union[None, Position], error_name:Union[str, None], details:Union[str, None]):
    self.pos_start = pos_start
    self.pos_end = pos_end
    self.error_name = error_name
    self.details = details

  def as_string(self):
    result = f'{self.error_name}: {self.details}'
    result += f'\n\nFile {self.pos_start.fn}, line {self.pos_start.ln + 1}, column {self.pos_start.col + 1}:{self.pos_end.col}\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
    return colored(result, "red")

class IllegalCharError(Error):
  def __init__(self, pos_start:Union[None, Position], pos_end:Union[None, Position], details=""):
    super().__init__(pos_start, pos_end, 'Illegal Character', details)

class ExpectedCharacterError(Error):
  def __init__(self, pos_start:Union[None, Position], pos_end:Union[None, Position], details=""):
    super().__init__(pos_start, pos_end, 'Expected Character', details)

class InvalidSyntaxError(Error):
  def __init__(self, pos_start:Union[None, Position], pos_end:Union[None, Position], details=""):
    super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

class RTError(Error):
  def __init__(self, pos_start:Union[None, Position], pos_end:Union[None, Position], details="", context:Union[Context, None]=None):
    super().__init__(pos_start, pos_end, 'Runtime error', details)
    self.context:Union[Context, None] = context

  def as_string(self):
    result = self.generate_traceback()
    result += f'{self.error_name}: {self.details}'
    result += f'\n\nFile {self.pos_start.fn}, line {self.pos_start.ln + 1}, column {self.pos_start.col + 1}:{self.pos_end.col}\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
    return colored(result, "red")

  def generate_traceback(self):
    result = ""
    pos = self.pos_start
    ctx = self.context

    while ctx:
      result = f"  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n" + result
      pos = ctx.parent_entry_pos
      ctx = ctx.parent

    return "Traceback (most recent call last):\n" + result
