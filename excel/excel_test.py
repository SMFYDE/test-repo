"""
This script is to test OpenPyXL
"""

import openpyxl


class ExcelEngine():
    def __init__(
        self,
    ) -> None:
        self.workbook = openpyxl.Workbook("pattern.xlsx")
        self.sheet = self.workbook.active

    def edit_one_cell(
        self,
        cell,
        value
    ) -> None:
        self.sheet[cell] = value

    def save(
        self
    ) -> None:
        self.workbook.save('hello_world.xlsx')
        self.workbook.close()


excel_engine = ExcelEngine()
excel_engine.edit_one_cell(
    'A1', 'Hello'
)
excel_engine.edit_one_cell(
    'B1', 'World'
)
excel_engine.save()
