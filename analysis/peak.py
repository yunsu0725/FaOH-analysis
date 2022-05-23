from analysis.sheet_manager import SheetManager
from pathlib import Path
import analysis.utils as utils


def pick_peak(RT_dict: dict, sheet_manager: SheetManager, data_dir: Path):
    work_sheet = sheet_manager.load_peak_id_sheet()
    df = sheet_manager.load_john_code_data_frames()
    # Preparing list of strings called Vial_names where each element is the name of a sample
    txt_files = utils.get_all_txt_files(data_dir)
    Vial_names = utils.get_vial_names(txt_files)
    # Create list of analytes to make it easy to call dictionary in future
    analytes = RT_dict.keys()

    # This block goes through the dataframe from the John_Code sheet and picks out sample names and relevant peaks.
    txt_file_headers = ['R.time', 'I.time',
                        'F.time', 'Area', 'Height', 'Peak_ID']

    for i in range(len(df)):
        # picks out each row in dataframe and truncates - would be more elegant to not have to use dataframe but whatever
        row_calling = df.loc[i, :]
        vals = row_calling.values.tolist()
        vals = vals[0:6]

        y = type(vals[0])

        if vals[0] in Vial_names:
            sample_of_interest = 'yes'
            # picks out sample names and adds to worksheet
            heading = [vals[0] for _ in range(6)]
            work_sheet.append(heading)
            work_sheet.append(txt_file_headers)

        elif vals[0] != 'Peak#' and y == str:
            sample_of_interest = 'no'

        # picks out peaks
        x = type(vals[1])
        if x == int:  # This if statement is for the rare occasion when the retention time of an analyte is an integer
            vals[1] = float(vals[1])
            x = type(vals[1])

        if x == float and sample_of_interest == 'yes':
            for a in analytes:
                upper_tolerance = RT_dict[a] + 0.1
                lower_tolerance = RT_dict[a] - 0.1
                if vals[1] < upper_tolerance and vals[1] > lower_tolerance:
                    vals.append(a)
                    work_sheet.append(vals[1:])

    sheet_manager.save_workbook()


def calc_quant_sheet(sheet_manager: SheetManager):
    peak_id_sheet = sheet_manager.load_peak_id_sheet()
    quant_sheet = sheet_manager.load_quant_sheet()
    cur_peak_id, cur_area = None, None

    quant_sheet_list = []
    # iterates through a semi-arbitrary number of rows and only reports values, still a tuple
    for row in peak_id_sheet.iter_rows(min_row=1, max_row=5000, min_col=1, max_col=10, values_only=True):

        if utils.get_peak_id_from_row(row) == cur_peak_id:
            # If there is a duplicate label for a single peak,
            # pick the peak with the larger area
            if utils.get_area_from_row(row) > cur_area:
                quant_sheet_list.pop()
                quant_sheet_list.append(row)
            else:
                continue
        else:
            quant_sheet_list.append(row)

        # breaks out of for loop once all text file data is iterated through
        if utils.get_area_from_row(row) is None:
            break
        cur_peak_id, cur_area = utils.get_peak_id_from_row(
            row), utils.get_area_from_row(row)

    for row in quant_sheet_list:
        quant_sheet.append(row)

    sheet_manager.save_workbook()


def calc_quant_full(sheet_manager: SheetManager, analytes):
    sheet_read = sheet_manager.load_peak_id_sheet()
    quant_full_sheet = sheet_manager.load_quant_full_sheet()
    sample_header = []
    data_header = ['R.time', 'I.time', 'F.time', 'Area', 'Height', 'Peak_ID']

    # iterates through a semi-arbitrary number of rows and only reports values, still a tuple
    for row in sheet_read.iter_rows(min_row=1, max_row=sheet_read.max_row, min_col=1, max_col=10, values_only=True):
        # This is a bit clunky, but it ensures the order of the samples in the Peak_ID tab is maintained
        if row[0] is not None and row[0] == row[1] == row[2]:
            sample_header = [row[0] for _ in range(6)]
            quant_full_sheet.append(sample_header)
            quant_full_sheet.append(data_header)
            for a in analytes:
                blank_row = [0, 0, 0, 0, 0, a]
                quant_full_sheet.append(blank_row)

    quant_sheet = sheet_manager.load_quant_sheet()
    fat_ass = True
    last_count = 1
    while fat_ass:
        counter = 0
        for row2, row3 in zip(
            quant_sheet.iter_rows(
                min_row=1, max_row=quant_full_sheet.max_row, min_col=1, max_col=10, values_only=True
            ),
            quant_full_sheet.iter_rows(
                min_row=1, max_row=quant_full_sheet.max_row, min_col=1, max_col=10, values_only=True
            )
        ):
            counter = counter + 1
            if counter < last_count:
                continue

            if utils.get_peak_id_from_row(row2) == utils.get_peak_id_from_row(row3):
                last_count = counter
            else:
                quant_sheet.insert_rows(counter)
                quant_sheet.cell(
                    row=counter, column=6).value = utils.get_peak_id_from_row(row3)
                quant_sheet.cell(row=counter, column=5).value = 0.000000001
                break

            if counter == quant_full_sheet.max_row:
                fat_ass = False
                break
            else:
                continue

    sheet_manager.save_workbook()
