from dataclasses import dataclass


@dataclass
class DataPoint:
    peak_id: int
    r_time: float
    i_time: float
    f_time: float
    area: float
    height: float
    chain_name: str = None  # it is unknown while reading from the txt files

    def get_raw_data_row(self) -> list:
        return [
            self.peak_id, self.r_time, self.i_time, self.f_time, self.area, self.height
        ]

    @classmethod
    def get_raw_data_sheet_header(cls) -> list[str]:
        return ['Peak#', 'R.Time', 'I.Time', 'F.Time', 'Area', 'Height']

    @classmethod
    def get_quantification_sheet_header(cls) -> list[str]:
        return ['R.time', 'I.time', 'F.time', 'Area', 'Height', 'Peak_ID']

    def get_quantification_sheet_row(self) -> list:
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


def get_chain_names(data_points: list[DataPoint]) -> list[str]:
    return [dp.chain_name for dp in data_points if dp.chain_name is not None]


def pad_missing_chain(
    data_points: list[DataPoint],
    analytes: list[str]
) -> list[DataPoint]:
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
