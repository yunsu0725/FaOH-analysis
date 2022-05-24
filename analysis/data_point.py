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
