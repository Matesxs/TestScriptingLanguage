from basic.symbol_table import SymbolTable
from typing import Union

class Context:
  def __init__(self, display_name:str, parent=None, parent_entry_pos=None):
    self.display_name = display_name
    self.parent = parent
    self.parent_entry_pos = parent_entry_pos
    self.symbol_table:Union[SymbolTable, None] = None