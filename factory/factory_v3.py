"""
"""

import importlib.machinery
import inspect

module = importlib.machinery.SourceFileLoader("Name", './factory/extraction_output_pattern.py').load_module()
class_members = inspect.getmembers(module, inspect.isclass)

for name, cls in class_members:
    print(f"Class members in module: {name} - {cls}")
    print(f"Class name: {cls.name if hasattr(cls, 'name') else 'No name attribute'}")
    print('-' * 20)
