from dataclasses import dataclass
from typing import List


@dataclass
class DataPoint:
    peak_id: int  # FIXME: maybe we don't need it since it is not concerned?
    r_time: float
    i_time: float
    f_time: float
    area: float
    height: float
    chain_name: str = None  # it is unknown while reading from the txt files
    conc: int = None # it is None unless the dp belong to a alc_acid_id label, such as FaOH-100 (conc = 100 here)

    def get_raw_data_row(self) -> List:
        return [
            self.peak_id, self.r_time, self.i_time, self.f_time, self.area, self.height
        ]

    @classmethod
    def get_raw_data_sheet_header(cls) -> List[str]:
        return ['Peak#', 'R.Time', 'I.Time', 'F.Time', 'Area', 'Height']

    @classmethod
    def get_quantification_sheet_header(cls) -> List[str]:
        return ['R.time', 'I.time', 'F.time', 'Area', 'Height', 'Peak_ID']

    def get_quantification_sheet_row(self) -> List:
        return [
            self.r_time, self.i_time, self.f_time, self.area, self.height, self.chain_name
        ]

    def __lt__(self, other):
        # it defines the 'less than' relation, which is called implicitly while
        # sorint the list. We cannot directly compare the strings because
        # 'C2' > 'C11' but we actually expect 2 < 11 while ordering

        if self.chain_name is None:
            return True
        if other.chain_name is None:
            return False

        # C11 -> 11, so index starts from 1
        my_idx = int(self.chain_name[1:])
        other_idx = int(other.chain_name[1:])
        return my_idx < other_idx


def parse_data_point_from_quant_sheet_row(df_row: List[float]) -> DataPoint:
    """generate a data point from a given quant sheet row

    Args:
        df_row (List[float]): a row of the data frame

    Returns:
        DataPoint: corresponding data point, might be None if the df_row is invalid
    """
    try:
        dp = DataPoint(
            peak_id=df_row[5],
            chain_name=df_row[5],
            r_time=float(df_row[0]),
            i_time=float(df_row[1]),
            f_time=float(df_row[2]),
            area=float(df_row[3]),
            height=float(df_row[4])
        )
        return dp
    except (IndexError, ValueError):
        # TODO: error logger
        return None


def get_chain_names(data_points: List[DataPoint]) -> List[str]:
    return [dp.chain_name for dp in data_points if dp.chain_name is not None]


def pad_missing_chain(
    data_points: List[DataPoint],
    analytes: List[str]
) -> List[DataPoint]:
    chain_names = set(get_chain_names(data_points))
    missing_chains = [a for a in analytes if a not in chain_names]
    pad = [
        DataPoint(
            peak_id=0,
            r_time=0,
            i_time=0,
            f_time=0,
            area=0,
            height=0,
            chain_name=chain_name
        )
        for chain_name in missing_chains
    ]
    res = data_points + pad
    res.sort()
    return res
