from pathlib import Path
import openpyxl


class SheetManager:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.john_code_key = 'John_Code'
        self.peak_id_key = 'Peak_ID'
        self.wb = openpyxl.Workbook()

    def create(self):
        self.wb.create_sheet(title=self.john_code_key)
        self.wb.create_sheet(title=self.peak_id_key)

    def load_john_code_sheet(self):
        return self.wb[self.john_code_key]

    def load_peak_id_sheet(self):
        return self.wb[self.peak_id_key]

    def save_workbook(self):
        self.wb.save(self.file_path)
