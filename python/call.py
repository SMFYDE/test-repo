"""
"""

import fcts

for func_name in dir(fcts):
    if callable(getattr(fcts, func_name)) and not func_name.startswith("__"):
        func = getattr(fcts, func_name)
        print(f"Calling {func_name}: {func()}")
