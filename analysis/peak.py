from analysis.data_point import DataPoint
from typing import Dict, List


def filter_unselected_points(data_points: List[DataPoint]) -> List[DataPoint]:
    return [dp for dp in data_points if dp.chain_name is not None]


def filter_duplicate_chain(dp_list: List[DataPoint]) -> List[DataPoint]:
    selected_dp = {}
    for dp in dp_list:
        if (c := dp.chain_name) not in selected_dp:
            selected_dp[c] = dp
        elif selected_dp[c].area < dp.area:
            selected_dp[c] = dp
    res = [x for x in selected_dp.values()]
    return sorted(res, key=lambda x: x.get_chain_index())


def pick_peaks(
    dp_dict: Dict[str, List[DataPoint]],
    rt: Dict[str, float],
    analytes: List[str],
    vial_names: List[str],
    threshold: float,
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
                upper_tolerance = rt[a] + threshold
                lower_tolerance = rt[a] - threshold
                if lower_tolerance < dp.r_time < upper_tolerance:
                    dp.chain_name = a

    def filter_points(dp: List[DataPoint]) -> List[DataPoint]:
        # drop those data points not binded with any peak (ie the chain name is not set)
        selected_dp = filter_unselected_points(dp)
        # remove the duplicate peaks
        unique_dp = filter_duplicate_chain(selected_dp)
        return unique_dp

    res = {
        key: filter_points(dp) for key, dp in dp_dict.items()
    }
    return res
