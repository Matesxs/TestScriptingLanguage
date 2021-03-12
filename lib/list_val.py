from .basic.error import RTError
from . import Value
from . import Number

class List(Value):
  def __init__(self, elements:list):
    super(List, self).__init__()
    self.elements = elements

  def recent(self):
    try:
      return self.elements[-1], None
    except:
      return None, RTError(self.pos_start, self.pos_end, "Cant get recent value from empty list")

  def added_to(self, other):
    new_list = self.copy()
    if isinstance(other, List):
      new_list.elements.extend(other.elements)
    else:
      new_list.elements.append(other)

    return new_list, None

  def multed_by(self, other):
    if isinstance(other, Number):
      new_list = self.copy()
      new_list.elements *= other.value
      return new_list, None
    else:
      return None, self.illegal_operation(other)

  def subbed_by(self, other):
    if isinstance(other, Number):
      new_list = self.copy()
      try:
        new_list.elements.pop(other.value)
        return new_list, None
      except:
        return None, RTError(other.pos_start, other.pos_end, "Index to the list is out of bounds")
    else:
      return None, self.illegal_operation(other)

  def dived_by(self, other):
    if isinstance(other, Number):
      try:
        return self.elements[other.value], None
      except:
        return None, RTError(other.pos_start, other.pos_end, "Index to the list is out of bounds")
    else:
      return None, self.illegal_operation(other)

  def copy(self):
    return List(self.elements[:]).set_context(self.context).set_position(self.pos_start, self.pos_end)

  def __repr__(self):
    return str(self.elements)