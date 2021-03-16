from typing import Union
from .error import ErrorBase

class RTResult:
  def __init__(self):
    self.value = None
    self.error: Union[None, ErrorBase] = None
    self.func_ret_val = None
    self.loop_should_continue = False
    self.loop_should_break = False

  def reset(self):
    self.value = None
    self.error: Union[None, ErrorBase] = None
    self.func_ret_val = None
    self.loop_should_continue = False
    self.loop_should_break = False

  def register(self, res):
    self.error = res.error
    self.func_ret_val = res.func_ret_val
    self.loop_should_continue = res.loop_should_continue
    self.loop_should_break = res.loop_should_break
    return res.value

  def success(self, value):
    self.reset()
    self.value = value
    return self

  def success_return(self, value):
    self.reset()
    self.func_ret_val = value
    return self

  def success_continue(self):
    self.reset()
    self.loop_should_continue = True
    return self

  def success_break(self):
    self.reset()
    self.loop_should_break = True
    return self

  def failure(self, error:ErrorBase):
    self.reset()
    self.error = error
    return self

  def should_return(self):
    return self.error or self.func_ret_val or self.loop_should_continue or self.loop_should_break