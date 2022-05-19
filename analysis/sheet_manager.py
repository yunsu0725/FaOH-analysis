from pathlib import Path
from xlsxwriter import Workbook
import openpyxl


class SheetManager:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.john_code_key = 'John_Code'
        self.peak_id_key = 'Peak_ID'

    def create(self):
        wb = Workbook(self.file_path)
        wb.add_worksheet(self.john_code_key)
        wb.add_worksheet(self.peak_id_key)

    def load_workbook(self) -> Workbook:
        return openpyxl.load_workbook(self.file_path)

    def load_john_code_sheet(self):
        wb = self.load_workbook()
        return wb[self.john_code_key]

    def load_peak_id_sheet(self):
        wb = self.load_workbook()
        return wb[self.peak_id_key]
