import sys
import os
from entry_point import run

if __name__ == '__main__':
  if len(sys.argv) == 1:
    while True:
      text = input('>> ')
      result, error = run('<stdin>', text)

      if error: print(error.as_string())
      elif result:
        if len(result.elements) == 1:
          print(repr(result.elements[0]))
        else:
          print(repr(result))
  else:
    if os.path.exists(sys.argv[1]) and os.path.isfile(sys.argv[1]):
      with open(sys.argv[1], "r") as f:
        script = f.read()
        _, error = run(sys.argv[1], script)

        if error:
          print(error.as_string())