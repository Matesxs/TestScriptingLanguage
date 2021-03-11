class SymbolTable:
  def __init__(self):
    self.symbols = {}
    self.protected_names = []
    self.parent = None

  def get(self, name:str):
    value = self.symbols.get(name, None)

    if value is None and self.parent is not None:
      return self.parent.get(name, None)

    return value

  def set(self, name:str, value, protected:bool=False):
    if name in self.protected_names: return False

    self.symbols[name] = value

    if protected and name not in self.protected_names:
      self.protected_names.append(name)
    return True

  def delete(self, name:str):
    if name in self.protected_names: return False
    del self.symbols[name]
    return True