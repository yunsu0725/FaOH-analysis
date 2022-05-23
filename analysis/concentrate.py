import pandas as pd
import numpy as np
import math
from analysis.sheet_manager import SheetManager
from openpyxl.utils.dataframe import dataframe_to_rows


def calc_area_conc_scale(sheet_manager: SheetManager):
    sheet_input = sheet_manager.load_external_standard_sheet()
    numCols = len(sheet_input[1])
    res = dict()
    # Parses through external standard concentrations from EXT_STD tab and outputs the variables to be copied into below block
    for row in sheet_input.iter_rows(min_row=2, max_row=100, min_col=1, max_col=numCols):
        label = row[0].value
        if label is None:
            continue
        # conc and peak area appear alternatively in the row
        try:
            # TODO: check w/ yun so see if float is allowed here
            area = [int(x.value) for x in row[2:numCols:2]]
            conc = [int(x.value) for x in row[1:numCols:2]]
            res[label] = np.polyfit(conc, area, 1)[0]
        except ValueError:
            print(f'Invalid area or conc for: {label}')
    print(f'{res=}')
    return res


def calc_and_concentrate_data(sheet_manager: SheetManager):
    # dictionary of internal standard concentrations
    # TODO: check if we configure this dict, if so, put it in the yaml
    int_std_conc = {'C3': 50, 'C5': 50, 'C7': 50, 'C9': 50,
                    'C11': 50, 'C13': 50, 'C15': 50, 'C17': 50}
    # dictionary of scale factors to turn area data into concentration data
    scale = calc_area_conc_scale(sheet_manager)
    orig = sheet_manager.load_quant_sheet_data_frame()

    # TODO: avoid the magic indices here: 3 -> area 5 -> peak id
    df = sheet_manager.load_quant_sheet_data_frame([3, 5])

    # FIXME: what are they for?
    # add 4 empty columns
    df['Pfleger'] = ""
    df['Lab'] = ""
    df['For'] = ""
    df['Life'] = ""

    dfList = df.values.tolist()
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
            if dfList[row][2] != "" and int(chain[-1]) % 2 == 1:
                dfList[row][3] = dfList[row][2]/int_std_conc[chain]

    # Calculate Averaged Scaling Factors and Corrected Concentrations
    for row in range(len(dfList)):
        chain = dfList[row][1]
        area = dfList[row][0]
        if (isinstance(area, float) or isinstance(area, int)) and dfList[row][2] != "" and int(chain[len(chain)-1]) % 2 == 0:
            flanking = np.array(
                [dfList[row-1][3], dfList[row+1][3] if row +
                    1 < len(dfList) else dfList[row-1][3]]
            )
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
                # TODO: err handling
                pass

    # modify data type to allow python to write to excel
    dfList = np.array(dfList)
    concDataDict = {
        'Uncorrected Concentration': dfList[:, 2].tolist(),
        'Scaling Factor': dfList[:, 3].tolist(),
        'Averaged Scaling Factor': dfList[:, 4].tolist(),
        'Corrected Concentration': dfList[:, 5].tolist()
    }
    order = [
        'Uncorrected Concentration',
        'Scaling Factor',
        'Averaged Scaling Factor',
        'Corrected Concentration'
    ]
    concData = pd.DataFrame(concDataDict, columns=order)
    excelData = pd.concat([orig, concData], axis=1)

    # write to the workbook
    rows = dataframe_to_rows(excelData)
    sheet = sheet_manager.load_concentration_sheet()
    for r in rows:
        # omit the row index, which locates in r[0]
        sheet.append(r[1:])
    sheet_manager.save_workbook()
