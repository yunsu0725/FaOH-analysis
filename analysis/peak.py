from analysis.data_point import DataPoint
from typing import Dict, List


def filter_unselected_points(data_points: List[DataPoint]) -> List[DataPoint]:
    return [dp for dp in data_points if dp.chain_name is not None]


def pick_peaks(
    dp_dict: Dict[str, List[DataPoint]],
    rt: Dict[str, float],
    analytes: List[str],
    vial_names: List[str],
):
    # key is sth like FaOH-10 (the txt file name)
    for key, data_points in dp_dict.items():
        if key not in vial_names:
            # actually it shd not happens since both vial_names and the dp_dict are generated automatically
            # from the same txt files, but I still add this clause to hint unexpected error
            # TODO: warn logger
            continue

        for dp in data_points:
            for a in analytes:
                # a is sth like C3
                # TODO: make the threshold configurable
                upper_tolerance = rt[a] + 0.1
                lower_tolerance = rt[a] - 0.1
                if lower_tolerance < dp.r_time < upper_tolerance:
                    dp.chain_name = a

    # drop those data points not binded with any peak (ie the chain name is not set)
    res = {
        key: filter_unselected_points(data_points=dp) for key, dp in dp_dict.items()
    }
    return res
