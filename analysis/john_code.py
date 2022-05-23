from analysis.utils import get_all_txt_files
from analysis.sheet_manager import SheetManager


def extract_rows_from_file(file_path, work_sheet, row):
    with open(file_path, 'r') as f:
        reading_flag = False
        for line in f.readlines():
            columns = line.split()
            if line.startswith('Sample Name'):
                # there should be a line with format like 'Sample Name CM24-A'
                # which matches the condition here, and we want to get the sample name
                # after the prefix, as there might be blanks, we concat the columns left
                # I simplified the legacy conditions in the ipynb by using a concat idiom
                sample_name = ''.join(columns[2:])
                work_sheet.cell(row=row, column=1, value=sample_name)

            if line.startswith('Peak#'):
                reading_flag = True

            if reading_flag:
                if len(columns) > 1:
                    row = row+1
                    for c in range(6):
                        try:
                            val = float(columns[c])
                        except ValueError:
                            val = columns[c]
                        work_sheet.cell(row=row, column=c+1, value=val)
                else:
                    # the blank line separte the peak table and the following blocks
                    # we can break here since we only care about the peak table
                    break

    return row+2


def calc_john_code(data_dir: str, sheet_manager: SheetManager):
    work_sheet = sheet_manager.load_john_code_sheet()
    all_txt_files = get_all_txt_files(data_dir)
    # openpyxl writes cell starting from 1 instead of 0
    row = 1
    for file in all_txt_files:
        file_path = data_dir / file
        row = extract_rows_from_file(file_path, work_sheet, row)
    sheet_manager.save_workbook()
