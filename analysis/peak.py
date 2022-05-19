import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import xlwt
import openpyxl
from analysis.file_utils import get_vial_names, get_result_file_path


# change to the name you put in JohnCode
filename = 'GCFID-trc-tet-RBS-library-May2022.xlsx'


wb = openpyxl.load_workbook(filename)
sheet1 = ''
sheet1 = wb['John_Code']
sheet2 = ''
sheet2 = wb.create_sheet('Peak_ID')


df = pd.read_excel(filename, sheet_name='John_Code', header=None)


# Preparing list of strings called Vial_names where each element is the name of a sample

Vial_names = get_vial_names()

# FAOH Retention Times (minutes on FatWax column w Stabilwax protocol)


C3 = 4.080
C4 = 7.645
C5 = 12.622
C6 = 14.872
C7 = 16.310
C8 = 17.613
C9 = 18.648
C10 = 19.667
C11 = 20.660
C12 = 21.550
C13 = 22.340
C14 = 23.170
C15 = 23.920
C16 = 24.709
C17 = 25.464
C18 = 26.127

# Create a dictionary which can be updated by changing values above. The dictionary will be called in peak identification (next block)

RT_dict = {'C3': C3, 'C4': C4, 'C5': C5, 'C6': C6, 'C7': C7, 'C8': C8, 'C9': C9, 'C10': C10,
           'C11': C11, 'C12': C12, 'C13': C13, 'C14': C14, 'C15': C15, 'C16': C16, 'C17': C17, 'C18': C18}

# Create list of analytes to make it easy to call dictionary in future
analytes = ['C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10',
            'C11', 'C12', 'C13', 'C14', 'C15', 'C16', 'C17', 'C18']

# This block goes through the dataframe from the John_Code sheet and picks out sample names and relevant peaks.

num_rows = len(df)
row_name = list(range(0, num_rows))
txt_file_headers = ['R.time', 'I.time', 'F.time', 'Area', 'Height', 'Peak_ID']

for i in row_name:
    if i < num_rows+1:
        # picks out each row in dataframe and truncates - would be more elegant to not have to use dataframe but whatever
        row_calling = df.loc[i, :]
        vals = row_calling.values.tolist()
        vals = vals[0:6]

        y = type(vals[0])

        if vals[0] in Vial_names:
            sample_of_interest = 'yes'

            # picks out sample names and adds to worksheet
            print(vals[0])
            heading = [vals[0], vals[0], vals[0], vals[0], vals[0], vals[0]]
            print(heading)
            sheet2.append(heading)
            sheet2.append(txt_file_headers)

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
                    # print(vals[1])
                    vals.append(a)
                    # print(vals)
                    sheet2.append(vals[1:])

wb.save(filename)


wb = openpyxl.load_workbook(filename)
sheet2 = ''
sheet2 = wb['Peak_ID']
sheet3 = ''

sheet3 = wb.create_sheet('Quantification w IS,ES')

ID = 'blank'
Area = 'blank'
sheet3_list = []

# iterates through a semi-arbitrary number of rows and only reports values, still a tuple
for row in sheet2.iter_rows(min_row=1, max_row=5000, min_col=1, max_col=10, values_only=True):

    if row[5] == ID:  # If there is a duplicate label for a single peak, pick the peak with the larger area
        if row[3] > Area:
            sheet3_list.pop()
            sheet3_list.append(row)
        else:
            continue

    else:
        sheet3_list.append(row)

    if row[3] == None:  # breaks out of for loop once all text file data is iterated through
        break

    else:
        ID = row[5]
        Area = row[3]

for row in sheet3_list:
    sheet3.append(row)

# Notice that this code may not work as intended if there is a duplicate in the first row, however, since the first row will always be a sample name, it is fine.


wb.save(filename)


wb = openpyxl.load_workbook(filename)
sheet_read = ''
sheet_read = wb['Peak_ID']
sheet3 = ''
sheet3 = wb.create_sheet('Quantification w IS,ES-full')

sample_header = []
data_header = ['R.time', 'I.time', 'F.time', 'Area', 'Height', 'Peak_ID']

# iterates through a semi-arbitrary number of rows and only reports values, still a tuple
for row in sheet_read.iter_rows(min_row=1, max_row=sheet_read.max_row, min_col=1, max_col=10, values_only=True):
    # This is a bit clunky, but it ensures the order of the samples in the Peak_ID tab is maintained
    if row[0] == row[1] and row[1] == row[2]:
        sample = row[0]
        sample_header = [sample, sample, sample, sample, sample, sample]
        sheet3.append(sample_header)
        sheet3.append(data_header)
        for a in analytes:
            blank_row = [0, 0, 0, 0, 0, a]
            sheet3.append(blank_row)


print(sheet3.max_row)


#wb = openpyxl.load_workbook('GCData-JGI_ACRs.xlsx')
sheet2 = ''
sheet2 = wb['Quantification w IS,ES']
sheet3 = ''
sheet3 = wb['Quantification w IS,ES-full']

Ass_Fat = True
last_count = 1
while Ass_Fat:

    counter = 0

    for row2, row3 in zip(sheet2.iter_rows(min_row=1, max_row=sheet3.max_row, min_col=1, max_col=10, values_only=True), sheet3.iter_rows(min_row=1, max_row=sheet3.max_row, min_col=1, max_col=10, values_only=True)):
        #print(row1[0], row2[0])
        counter = counter + 1
        # print(counter)
        if counter < last_count:
            continue
        elif row2[5] == row3[5]:
            last_count = counter
            print(last_count)
        elif row2[5] != row3[5]:
            # print(row3[5])
            sheet2.insert_rows(counter)
            sheet2.cell(row=counter, column=6).value = row3[5]
            sheet2.cell(row=counter, column=5).value = 0.000000001
            #last_count = counter
            break

        if counter == sheet3.max_row:
            Ass_Fat = False
            break
        else:
            continue


#wb.remove_sheet('Quantification w IS,ES-full')
wb.save(filename)

# useless
for i, j in zip([1, 2, 3], [3, 2, 1]):
    print(i, j)
