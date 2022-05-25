import pandas as pd
from analysis.sheet_manager import SheetManager
from openpyxl.utils.dataframe import dataframe_to_rows
from typing import List


def get_alc_acid_indices(dfList: List, alc_acid_ID: str) -> List:
    # creates list of external standard title indicies (location of titles)
    def match(df) -> bool:
        if len(df) < 2:
            return False
        name = df[1]
        return name[:name.find('-')] == alc_acid_ID

    return [
        i for i, df in enumerate(dfList) if match(df)
    ]


def calc_external_std_data(sheet_manager: SheetManager, standards_used, alc_acid_ID):
    # TODO: avoid the magic indices here: 3 -> area 5 -> peak id
    data_frames = sheet_manager.load_quant_sheet_data_frame([3, 5])
    # convert dataframe to array to allow array traversals
    dfList = data_frames.values.tolist()
    # Master_dict will hold area and concentration data
    Master_dict = standards_used

    alc_acid_indicies = get_alc_acid_indices(dfList, alc_acid_ID)
    conc_array = []
    titleTypes = ['Peak#', 'R.Time', 'I.Time', 'F.Time', 'Area', 'Height']
    # start adding to master matrix here using indicies of titles
    # TODO: simplify the legacy code here
    for i in alc_acid_indicies:
        # find the position right before the start of a new set of data as indicated by a string
        endindex = i
        for _ in range(len(dfList[i:len(dfList)])):
            endindex += 1
            if endindex >= len(dfList):
                break
            testVar = dfList[endindex][0]
            if(isinstance(testVar, str) and testVar not in titleTypes):
                break
        # parse title to find concentration (gets the number after '-' in the title) and add to conc_array and sort
        conc = dfList[i][1][dfList[i][1].find('-')+1:len(dfList[i][1])]
        conc_array.append(int(conc))
        conc_array.sort()
        # for each chain, add the concentration and area data to the Master dictionary
        for j in range(endindex-i):
            if(isinstance(dfList[i+j][0], int)):
                conc_and_area = [conc, dfList[i+j][0]]
                Master_dict[dfList[i+j][1]].append(conc_and_area)

    # create master matrix holding arrays of area values
    num_conc, num_chain = len(conc_array), len(Master_dict)
    Master = [
        [0 for _ in range(num_conc*2+1)] for _ in range(num_chain+1)
    ]
    # populate column titles
    Master[0][0] = 'Chain Length'
    for i in range(1, num_conc*2+1):
        Master[0][i] = 'Peak Area' if i % 2 == 0 else 'Conc (mg/L)'

    # create matrix with desired layout as seen in Cell 2
    chain_iterator = 1
    for chain in Master_dict:
        conc_iterator = 1
        # label first column with chain
        Master[chain_iterator][0] = chain
        for conc in conc_array:
            area = []
            # search for correct area data
            for pair in Master_dict[chain]:
                if int(pair[0]) == conc:
                    area.append(pair[1])
                    break
            # this accounts for double-counting areas (only picks the largest one)
            area.sort(reverse=True)
            # this accounts for no area data
            if len(area) == 0:
                area = ['']
            # add to the master matrix
            Master[chain_iterator][conc_iterator] = conc
            conc_iterator += 1
            Master[chain_iterator][conc_iterator] = area[0]
            conc_iterator += 1
        chain_iterator += 1

    excelData = pd.DataFrame(data=Master, index=None)
    # set first row as header for aesthetics
    new_header = excelData.iloc[0]
    excelData = excelData[1:]
    excelData.columns = new_header

    sheet = sheet_manager.load_external_standard_sheet()
    rows = dataframe_to_rows(excelData)
    for i, r in enumerate(rows):
        # magic here: the row 1 dataframe is a frozen list
        # shd figure it out
        if i != 1:
            sheet.append(r[1:])


def calc_external_standards(sheet_manager: SheetManager, analytes):
    # sth like {'C3': [], 'C4': [],...,'C18': []}
    standards_used = {x: [] for x in analytes}
    # FAOH or FAME, assumes the format: <FAME/FAOH>-<Concentration>
    # e.g. FAOH-100 or FAME-2000
    alc_acid_ID = 'FaOH'
    calc_external_std_data(sheet_manager, standards_used, alc_acid_ID)
    sheet_manager.save_workbook()
