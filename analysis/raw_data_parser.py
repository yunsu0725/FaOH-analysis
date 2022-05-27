from analysis.utils import get_all_txt_files
from analysis.data_point import DataPoint
from typing import Dict, List


def parse_data_point_from_columns(columns: List) -> DataPoint:
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


def parse_data_points_from_raw_txt(data_dir: str) -> Dict:
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
