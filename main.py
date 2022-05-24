from analysis.raw_data_parser import process_raw_data, parse_data_points_from_raw_txt
from analysis.peak import calc_quant_full, calc_quant_sheet, pick_peak_from_data_points, pick_peak
from analysis.utils import ConfigManager, get_all_txt_files, get_vial_names
from analysis.external_data import calc_external_standards
from analysis.sheet_manager import SheetManager
from analysis.concentrate import calc_and_concentrate_data
from pathlib import Path


def new_flow():
    configManager = ConfigManager(Path('./exp.yml'))
    sheet_manager = SheetManager(configManager.get_result_file_path())
    sheet_manager.create()
    data_dir = configManager.get_data_dir()
    all_txt_files = get_all_txt_files(data_dir)
    vial_names = get_vial_names(all_txt_files)

    process_raw_data(data_dir, sheet_manager)
    data_points = parse_data_points_from_raw_txt(data_dir)
    # print(f'{data_points=}')
    sheet_manager.write_raw_data_points(data_points, vial_names)

    rt = configManager.get_retention_times()
    analytes = rt.keys()

    peak_dp = pick_peak_from_data_points(data_points, rt, analytes, vial_names)
    for key, dps in peak_dp.items():
        print(f'{key=}')
        for dp in dps:
            print(f'  {dp=}')
            
    sheet_manager.save_workbook()


def cur_flow():
    configManager = ConfigManager(Path('./exp.yml'))
    sheet_manager = SheetManager(configManager.get_result_file_path())
    sheet_manager.create()
    data_dir = configManager.get_data_dir()
    process_raw_data(data_dir, sheet_manager)
    rt = configManager.get_retention_times()
    analytes = rt.keys()
    # pick_peak(data_dir, sheet_manager, rt, analytes)
    calc_quant_sheet(sheet_manager)
    calc_quant_full(sheet_manager, analytes)
    calc_external_standards(sheet_manager, analytes)
    int_std_conc = configManager.get_internal_std_conc()
    calc_and_concentrate_data(sheet_manager, int_std_conc)
    sheet_manager.drop_tmp_sheets()


if __name__ == '__main__':
    new_flow()
    # cur_flow()
