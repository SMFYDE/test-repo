"""
This script is to test OpenPyXL
"""

import openpyxl


class ExcelEngine():
    def __init__(
        self,
    ) -> None:
        self.workbook = openpyxl.load_workbook("pattern.xlsx")
        self.sheet = self.workbook.active

    def edit_one_cell(
        self,
        cell,
        value
    ) -> None:
        self.sheet[cell] = value

    def add_value_at_one_cell(
        self,
        cell,
        value
    ) -> None:
        self.sheet[cell].value += value

    def save(
        self
    ) -> None:
        self.workbook.save('hello_world.xlsx')
        self.workbook.close()


excel_engine = ExcelEngine()
excel_engine.add_value_at_one_cell(
    'B8', 'Hello'
)
excel_engine.save()
