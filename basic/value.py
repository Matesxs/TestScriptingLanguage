from typing import Union
from basic.position import Position
from basic.context import Context
from basic.error import RTError
from basic.runtime_result import RTResult

class Value:
  def __init__(self):
    self.pos_start:Union[Position, None] = None
    self.pos_end:Union[Position, None] = None
    self.context:Union[Context, None] = None

  def set_position(self, pos_start:Union[None, Position]=None, pos_end:Union[None, Position]=None):
    self.pos_start = pos_start
    self.pos_end = pos_end
    return self

  def set_context(self, context:Union[Context, None]=None):
    self.context = context
    return self

  def added_to(self, other):
    return None, self.illegal_operation(other)

  def subbed_by(self, other):
    return None, self.illegal_operation(other)

  def multed_by(self, other):
    return None, self.illegal_operation(other)

  def dived_by(self, other):
    return None, self.illegal_operation(other)

  def powed_by(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_eq(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_ne(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_lt(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_gt(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_lte(self, other):
    return None, self.illegal_operation(other)

  def get_comparison_gte(self, other):
    return None, self.illegal_operation(other)

  def anded_by(self, other):
    return None, self.illegal_operation(other)

  def ored_by(self, other):
    return None, self.illegal_operation(other)

  def notted(self):
    return None, self.illegal_operation()

  def execute(self, args, interpreter):
    return RTResult().failure(self.illegal_operation())

  def copy(self):
    raise Exception('No copy method defined')

  def is_true(self):
    return False

  def illegal_operation(self, other=None):
    if not other: other = self
    return RTError(self.pos_start, other.pos_end, 'Illegal operation', self.context)
