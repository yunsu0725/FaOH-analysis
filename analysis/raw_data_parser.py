from analysis.utils import get_all_txt_files
from analysis.sheet_manager import SheetManager
from analysis.data_point import DataPoint


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


def process_raw_data(data_dir: str, sheet_manager: SheetManager):
    work_sheet = sheet_manager.load_raw_sheet()
    all_txt_files = get_all_txt_files(data_dir)
    # openpyxl writes cell starting from 1 instead of 0
    row = 1
    for file in all_txt_files:
        file_path = data_dir / file
        row = extract_rows_from_file(file_path, work_sheet, row)
    sheet_manager.save_workbook()


def parse_data_point_from_columns(columns: list) -> DataPoint:
    # Row format recorded in the txt files is as below
    # Peak#	R.Time	I.Time	F.Time	Area	Height
    try:
        dp = DataPoint(
            peak_id=int(columns[0]),
            r_time=float(columns[1]),
            i_time=float(columns[2]),
            f_time=float(columns[3]),
            area=float(columns[4]),
            height=float(columns[5]),
        )
        return dp
    except (IndexError, ValueError):
        # TODO: error logger
        return None


def parse_data_points_from_raw_txt(data_dir: str) -> dict:
    all_txt_files = get_all_txt_files(data_dir)
    res = dict()
    for file in all_txt_files:
        file_path = data_dir / file
        reading_peak_table = False
        with open(file=file_path, mode='r') as f:
            data_points, chain_name = [], None
            for line in f:
                columns = line.split()
                if line.startswith('Sample Name'):
                    # there should be a line with format like 'Sample Name CM24-A'
                    # which matches the condition here, and we want to get the sample name
                    # after the prefix, as there might be blanks, we concat the columns left
                    chain_name = ''.join(columns[2:])
                    res[chain_name] = list()
                elif line.startswith('Peak#'):
                    reading_peak_table = True
                    continue

                if reading_peak_table:
                    if len(columns) > 1:
                        if (dp := parse_data_point_from_columns(columns)) and dp is not None:
                            data_points.append(dp)
                    else:
                        # the blank line separte the peak table and the following blocks
                        # we can break here since we only care about the peak table
                        res[chain_name] = data_points
                        break

    return res
