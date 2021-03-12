from .basic import Value
from . import Number

class String(Value):
  def __init__(self, value:str):
    super(String, self).__init__()
    self.value = value

  def added_to(self, other):
    if isinstance(other, String):
      return String(self.value + other.value).set_context(self.context), None
    else:
      return None, self.illegal_operation(other)

  def multed_by(self, other):
    if isinstance(other, Number):
      return String(self.value * other.value).set_context(self.context), None
    else:
      return None, self.illegal_operation(other)

  def is_true(self):
    return len(self.value) > 0

  def copy(self):
    return String(self.value).set_position(self.pos_start, self.pos_end).set_context(self.context)

  def __repr__(self):
    return f"\"{self.value}\""