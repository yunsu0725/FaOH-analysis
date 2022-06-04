from analysis.data_point import DataPoint
from typing import Dict, List


def vial_matches_alc_acid_id(vial: str, alc_acid_id: str):
    # Example: FaOH-10 will match the alc_acid_id FaOH here.
    return vial[:vial.find('-')] == alc_acid_id


def get_dp_subset_by_alc_acid_id(
    dp_dict: Dict[str, List[DataPoint]],
    alc_acid_id: str
) -> Dict[str, List[DataPoint]]:
    # filter those key (vial) not matches the alc_acid_id
    res = {
        vial: dp_list for vial, dp_list in dp_dict.items() if vial_matches_alc_acid_id(vial, alc_acid_id)
    }
    return res


def get_vial_conc(vial_label: str) -> int:
    cut_index = vial_label.find('-') + 1
    # 'FaOH-100' -> '100'
    conc_str = vial_label[cut_index:]
    # TODO: err handling probably?
    return int(conc_str)



def calc_external_std_data(
    dp_dict: Dict[str, DataPoint],
    alc_acid_id: str,
    analytes: List[str]
):
    dp_subset = get_dp_subset_by_alc_acid_id(dp_dict, alc_acid_id)
    print(f'{dp_subset.keys()=}')
    conc_num = len(dp_subset.keys())
    res = {
        a: [] for a in analytes
        # example: 'C3': List[DataPoint]
    }
    for vial, dp_list in dp_subset.items():
        conc = get_vial_conc(vial)
        for dp in dp_list:
            dp.conc = conc
            res[dp.chain_name].append(dp)

    return res, conc_num

