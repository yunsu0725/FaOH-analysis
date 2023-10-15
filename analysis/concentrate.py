import pandas as pd
import re
import numpy as np
import math
from analysis.sheet_manager import SheetManager
from openpyxl.utils.dataframe import dataframe_to_rows
from string import ascii_uppercase


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

    res = []
    aggregator = DataAggregator()
    # write to the workbook
    rows = dataframe_to_rows(excelData)
    base, sample = None, None
    for r in rows:
        if r[0] is None:
            # only append data
            continue
        label = r[1]
        if re.match(r'C\d+$', label):
            if is_internal_condition(label):
                # The regular expression matches labels like C1, C2,...,CN where N is a nature number
                # So it captures those chain labels here.
                # Moreover, we'd like to ignore those internal standard conc
                # since there are no meaningful corrected concentration values for them
                continue
            elif sample is not None:
                print(f'{base=} {sample=}, {r[1:]}')
                aggregator.add_data(base, sample, r[1:])
        elif label == 'Peak_ID':
            # TODO: refactor here, it's just a workaround to label the header
            r[2] = 'Corrected Concentration'
        else:
            base, sample = split_sample_label(label)

        # omit the row index, which locates in r[0]
        res.append(r[1:])
    print(f'{aggregator.data=}')
    print(f'{aggregator.get_repeats()=}')
    aggregator.output_to_sheet(sheet_manager)
    return res


class DataAggregator:
    def __init__(self):
        self.data = {}
        self.columns = [
            'C4', 'C6', 'C8', 'C10', 'C12', 'C14', 'C16', 'C18'
        ]
        self.sample_labels = list(ascii_uppercase)

    def add_data(self, base: str, sample: str, c):
        if len(c) != 2:
            print(f"error, {c=}")
            return

        key, value = c[0], c[1]
        if base not in self.data:
            self.data[base] = {}
        if sample not in self.data[base]:
            self.data[base][sample] = {}
        self.data[base][sample][key] = value

    def get_repeats(self):
        repeat_labels = set()
        for baseData in self.data.values():
            for label in baseData.keys():
                repeat_labels.add(label)
        print(f'{repeat_labels=}')
        return len(repeat_labels)

    def get_sample_value(self, base, sample, c_key):
        if base not in self.data:
            return None
        if sample not in self.data[base]:
            return None
        if c_key not in self.data[base][sample]:
            return None
        return self.data[base][sample][c_key]

    def output_to_sheet(self, sheet_manager: SheetManager):
        col_num = self.get_repeats()
        sheet = sheet_manager.load_titer_sheet()
        header = ['']
        for c in self.columns:
            header = header + [c] + [''] * (col_num-1)
        sheet.append(header)

        for base in self.data.keys():
            row = [base]
            for c_key in self.columns:
                for i in range(col_num):
                    sample = self.sample_labels[i]
                    data = self.get_sample_value(base, sample, c_key)
                    row.append(data)
            sheet.append(row)
        sheet_manager.save_workbook()


def split_sample_label(orig_label: str):
    if orig_label[-2] != "-" or not orig_label[-1].isalpha():
        return orig_label, None
    return orig_label[:-2], orig_label[-1]
