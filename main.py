from analysis.raw_data_parser import process_raw_data, parse_data_points_from_raw_txt
from analysis.peak import calc_quant_full, calc_quant_sheet, pick_peak
from analysis.utils import ConfigManager
from analysis.external_data import calc_external_standards
from analysis.sheet_manager import SheetManager
from analysis.concentrate import calc_and_concentrate_data
from pathlib import Path


if __name__ == '__main__':
    configManager = ConfigManager(Path('./exp.yml'))
    sheet_manager = SheetManager(configManager.get_result_file_path())
    sheet_manager.create()
    data_dir = configManager.get_data_dir()
    process_raw_data(data_dir, sheet_manager)
    x = parse_data_points_from_raw_txt(data_dir)
    print(f'{x=}')
    rt = configManager.get_retention_times()
    analytes = rt.keys()
    pick_peak(data_dir, sheet_manager, rt, analytes)
    calc_quant_sheet(sheet_manager)
    calc_quant_full(sheet_manager, analytes)
    calc_external_standards(sheet_manager, analytes)
    int_std_conc = configManager.get_internal_std_conc()
    calc_and_concentrate_data(sheet_manager, int_std_conc)
    sheet_manager.drop_tmp_sheets()
