from typing import Union
from .basic.error import RTError
from . import Value

class Number(Value):
  def __init__(self, value:Union[int, float]):
    super(Number, self).__init__()
    self.value = value
    if isinstance(self.value, float):
      int_val = int(self.value)
      if self.value == int_val:
        self.value = int_val

  def added_to(self, other):
    if isinstance(other, Number):
      return Number(self.value + other.value).set_context(self.context), None
    else:
      return None, self.illegal_operation(other)

  def subbed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value - other.value).set_context(self.context), None
    else:
      return None, self.illegal_operation(other)

  def multed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value * other.value).set_context(self.context), None
    else:
      return None, self.illegal_operation(other)

  def dived_by(self, other):
    if isinstance(other, Number):
      if other.value == 0: return None, RTError(other.pos_start, other.pos_end, "Division by zero", self.context)
      return Number(self.value / other.value).set_context(self.context), None
    else:
      return None, self.illegal_operation(other)

  def powed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value ** other.value).set_context(self.context), None
    else:
      return None, self.illegal_operation(other)

  def get_comparison_eq(self, other):
    if isinstance(other, Number):
      return Number(int(self.value == other.value)).set_context(self.context), None
    else:
      return None, self.illegal_operation(other)

  def get_comparison_ne(self, other):
    if isinstance(other, Number):
      return Number(int(self.value != other.value)).set_context(self.context), None
    else:
      return None, self.illegal_operation(other)

  def get_comparison_lt(self, other):
    if isinstance(other, Number):
      return Number(int(self.value < other.value)).set_context(self.context), None
    else:
      return None, self.illegal_operation(other)

  def get_comparison_gt(self, other):
    if isinstance(other, Number):
      return Number(int(self.value > other.value)).set_context(self.context), None
    else:
      return None, self.illegal_operation(other)

  def get_comparison_lte(self, other):
    if isinstance(other, Number):
      return Number(int(self.value <= other.value)).set_context(self.context), None
    else:
      return None, self.illegal_operation(other)

  def get_comparison_gte(self, other):
    if isinstance(other, Number):
      return Number(int(self.value >= other.value)).set_context(self.context), None
    else:
      return None, self.illegal_operation(other)

  def anded_by(self, other):
    if isinstance(other, Number):
      return Number(int(self.value and other.value)).set_context(self.context), None
    else:
      return None, self.illegal_operation(other)

  def ored_by(self, other):
    if isinstance(other, Number):
      return Number(int(self.value or other.value)).set_context(self.context), None
    else:
      return None, self.illegal_operation(other)

  def notted(self):
    return Number(1 if self.value == 0 else 0).set_context(self.context), None


  def is_true(self):
    return self.value != 0

  def copy(self):
    copy = Number(self.value)
    copy.set_position(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def __repr__(self):
    return str(self.value)