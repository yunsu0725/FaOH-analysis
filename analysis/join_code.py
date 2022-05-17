from sys import argv
import xlsxwriter
import os


def ExcelWriteRow(file_path, work_sheet, row):
    with open(file_path, 'r') as in_file:
        col = 0
        flag = False
        for line in in_file:
            columns = line.split()
            if len(columns) == 3 or len(columns) == 4:
                if columns[0] == 'Sample' and columns[1] == 'Name':
                    if len(columns) < 4:
                        work_sheet.write(row, col, columns[2])
                    else:
                        work_sheet.write(row, col, columns[2]+columns[3])
            if len(columns) > 1:
                if columns[0] == 'Peak#':
                    flag = True

            if flag == True:
                if len(columns) > 1:
                    row = row+1
                    # print(line)
                    for col in range(6):
                        try:
                            work_sheet.write(row, col, float(columns[col]))
                        except ValueError:
                            work_sheet.write(row, col, columns[col])
                else:
                    break

    return row+2


def WriteJohnCodeToXlsx(data_dir: str, file_path):
    workbook = xlsxwriter.Workbook(file_path)
    work_sheet = workbook.add_worksheet('John_Code')
    row = 0
    for _, _, files in os.walk(data_dir):
        for file in files:
            x = file.split('.')
            if len(x) > 1 and x[1].upper() == 'TXT':
                file_path = data_dir / file
                row = ExcelWriteRow(file_path, work_sheet, row)
    workbook.close()

