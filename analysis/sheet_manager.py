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
        self.external_standard_key = 'EXT_STD'
        self.concentration_key = 'Corrected Concentration'
        self.wb = openpyxl.Workbook()

    def create(self):
        self.wb.create_sheet(title=self.john_code_key)
        self.wb.create_sheet(title=self.peak_id_key)
        self.wb.create_sheet(title=self.quant_key)
        self.wb.create_sheet(title=self.quant_full_key)
        self.wb.create_sheet(title=self.external_standard_key)
        self.wb.create_sheet(title=self.concentration_key)
        del self.wb['Sheet']

    def load_john_code_sheet(self):
        return self.wb[self.john_code_key]

    def load_john_code_data_frames(self):
        df = pd.read_excel(
            self.file_path, sheet_name=self.john_code_key, header=None
        )
        return df

    def load_quant_sheet_data_frame(self, use_cols=None):
        df = pd.read_excel(
            self.file_path, sheet_name=self.quant_key, header=None, usecols=use_cols
        )
        return df

    def load_concentration_sheet(self):
        return self.wb[self.concentration_key]

    def load_peak_id_sheet(self):
        return self.wb[self.peak_id_key]

    def load_external_standard_sheet(self):
        return self.wb[self.external_standard_key]

    def load_quant_sheet(self):
        return self.wb[self.quant_key]

    def load_quant_full_sheet(self):
        return self.wb[self.quant_full_key]

    def drop_tmp_sheets(self):
        # it is a tmp workaround to drop the quant full sheet
        # we shd remove that sheet from the logic itself for long term if have time
        del self.wb[self.quant_full_key]
        self.save_workbook()

    def save_workbook(self):
        self.wb.save(self.file_path)
