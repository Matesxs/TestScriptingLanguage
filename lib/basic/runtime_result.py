from typing import Union
from .error.error import ErrorBase

class RTResult:
  def __init__(self):
    self.value = None
    self.error:Union[None, ErrorBase] = None

  def register(self, res):
    if res.error: self.error = res.error
    return res.value

  def success(self, value):
    self.value = value
    return self

  def failure(self, error:ErrorBase):
    self.error = error
    return self