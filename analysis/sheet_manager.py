from pathlib import Path
import openpyxl
import pandas as pd


class SheetManager:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.john_code_key = 'John_Code'
        self.peak_id_key = 'Peak_ID'
        self.quant_key = 'Quantification w IS,ES'
        self.quant_full_key = 'Quantification w IS,ES-full'
        self.wb = openpyxl.Workbook()

    def create(self):
        self.wb.create_sheet(title=self.john_code_key)
        self.wb.create_sheet(title=self.peak_id_key)
        self.wb.create_sheet(title=self.quant_key)
        self.wb.create_sheet(title=self.quant_full_key)
        del self.wb['Sheet']

    def load_john_code_sheet(self):
        return self.wb[self.john_code_key]

    def load_john_code_data_frames(self):
        df = pd.read_excel(
            self.file_path, sheet_name=self.john_code_key, header=None
        )
        return df

    def load_peak_id_sheet(self):
        return self.wb[self.peak_id_key]

    def load_quant_sheet(self):
        return self.wb[self.quant_key]

    def load_quant_full_sheet(self):
        return self.wb[self.quant_full_key]

    def save_workbook(self):
        self.wb.save(self.file_path)
