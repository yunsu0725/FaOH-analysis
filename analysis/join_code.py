from analysis.file_utils import get_all_txt_files
from analysis.sheet_manager import SheetManager


# TODO: simplify
def ExcelWriteRow(file_path, work_sheet, row):
    with open(file_path, 'r') as in_file:
        col = 1
        flag = False
        for line in in_file:
            columns = line.split()
            if len(columns) == 3 or len(columns) == 4:
                if columns[0] == 'Sample' and columns[1] == 'Name':
                    if len(columns) < 4:
                        work_sheet.cell(row=row, column=col, value=columns[2])
                    else:
                        work_sheet.cell(row=row, column=col,
                                        value=columns[2]+columns[3])
            if len(columns) > 1:
                if columns[0] == 'Peak#':
                    flag = True

            if flag == True:
                if len(columns) > 1:
                    row = row+1
                    # print(line)
                    for c in range(6):
                        try:
                            work_sheet.cell(row=row, column=c+1,
                                            value=float(columns[c]))
                        except ValueError:
                            work_sheet.cell(row=row, column=c +
                                            1, value=columns[c])
                else:
                    break

    return row+2


def WriteJohnCodeToXlsx(data_dir: str, sheet_manager: SheetManager):
    work_sheet = sheet_manager.load_john_code_sheet()
    all_txt_files = get_all_txt_files(data_dir)
    row = 1
    for file in all_txt_files:
        print(f'{file=}')
        file_path = data_dir / file
        row = ExcelWriteRow(file_path, work_sheet, row)
