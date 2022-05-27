import pandas as pd
import re
import numpy as np
import math
from analysis.sheet_manager import SheetManager
from openpyxl.utils.dataframe import dataframe_to_rows
from dataclasses import dataclass


def calc_area_conc_scale(sheet_manager: SheetManager):
    sheet_input = sheet_manager.load_external_standard_sheet()
    numCols = len(sheet_input[1])
    res = dict()
    # Parses through external standard concentrations from EXT_STD tab and outputs the variables to be copied into below block
    for row in sheet_input.iter_rows(
        min_row=2, max_row=100, min_col=1, max_col=numCols
    ):
        label = row[0].value
        if label is None:
            continue
        # conc and peak area appear alternatively in the row
        try:
            # TODO: check w/ yun so see if float is allowed here
            area = [float(x.value) for x in row[2:numCols:2]]
            conc = [float(x.value) for x in row[1:numCols:2]]
            res[label] = np.polyfit(conc, area, 1)[0]
        except ValueError:
            print(f'Invalid area or conc for: {label}')
    print(f'{res=}')
    return res


def is_internal_condition(chain: str) -> bool:
    # Pick internal standards to calculate scaling factors
    # for example:
    # C2 -> False, because 2 % 2 == 0
    # C3 -> True,  because 3 % 2 == 1
    return int(chain[-1]) % 2 == 1


def calc_and_concentrate_data(sheet_manager: SheetManager, int_std_conc: dict):
    scale = calc_area_conc_scale(sheet_manager)
    # TODO: avoid the magic indices here: 3 -> area 5 -> peak id
    orig = sheet_manager.load_quant_sheet_data_frame([5])
    df = sheet_manager.load_quant_sheet_data_frame([3, 5])
    # append four empty string
    dfList = [
        x + ['' for _ in range(4)] for x in df.values.tolist()
    ]
    # Calculate
    for row in range(len(dfList)):
        chain = dfList[row][1]
        area = dfList[row][0]
        # Calculate Uncorrected Concentration
        if isinstance(area, str) or math.isnan(area):
            dfList[row][2] = 0
        elif isinstance(area, float) or isinstance(area, int):
            dfList[row][2] = area/scale.get(chain)
            # Calculate Scaling Factor
            if is_internal_condition(chain):
                dfList[row][3] = dfList[row][2]/int_std_conc[chain]

    # Calculate Averaged Scaling Factors and Corrected Concentrations
    for row in range(len(dfList)):
        chain = dfList[row][1]
        area = dfList[row][0]
        if not isinstance(area, float) and not isinstance(area, int):
            continue

        if dfList[row][2] != "" and not is_internal_condition(chain):
            flanking = np.array([
                dfList[row-1][3],
                dfList[row+1][3] if row + 1 < len(dfList) else dfList[row-1][3]
            ])
            if flanking[0] == "":
                dfList[row][4] = flanking[1]
            elif flanking[1] == "":
                dfList[row][4] = flanking[0]
            else:
                dfList[row][4] = flanking.mean()
            try:
                uncorrected = float(dfList[row][2])
                avgscalefactor = float(dfList[row][4])
                # TODO: double check w/ yun
                if avgscalefactor != 0:
                    dfList[row][5] = uncorrected/avgscalefactor
            except ValueError:
                print(f'fail to calc average scale factor, {dfList[row]=}')

    # modify data type to allow python to write to excel
    dfList = np.array(dfList)
    # TODO: remove the legacy mapping here, they're just a note for devs
    # 'Uncorrected Concentration': 2
    # 'Scaling Factor': 3
    # 'Averaged Scaling Factor': 4
    # 'Corrected Concentration': 5
    concDataDict = {
        'Corrected Concentration': dfList[:, 5].tolist()
    }
    concData = pd.DataFrame(concDataDict)
    excelData = pd.concat([orig, concData], axis=1)

    # write to the workbook
    rows = dataframe_to_rows(excelData)
    sheet = sheet_manager.load_concentration_sheet()
    for r in rows:
        if r[0] is None:
            # only append data
            continue
        label = r[1]
        if re.match(r'C\d+', label) and is_internal_condition(label):
            # The regular expression matches labels like C1, C2,...,CN where N is a nature number
            # So it captures those chain labels here.
            # Moreover, we'd like to ignore those internal standard conc
            # since there are no meaningful corrected concentration values for them
            continue
        elif label == 'Peak_ID':
            # TODO: refactor here, it's just a workaround to label the header
            r[2] = 'Corrected Concentration'
        # omit the row index, which locates in r[0]
        sheet.append(r[1:])

    sheet_manager.save_workbook()
