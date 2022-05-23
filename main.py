from analysis.join_code import WriteJohnCodeToXlsx
from analysis.peak import calc_quant_full, calc_quant_sheet, pick_peak
from analysis.utils import ConfigManager
from analysis.external_data import calc_external_standards
from pathlib import Path

from analysis.sheet_manager import SheetManager


if __name__ == '__main__':
    configManager = ConfigManager(Path('./exp.yml'))
    sheet_manager = SheetManager(configManager.get_result_file_path())
    sheet_manager.create()
    data_dir = configManager.get_data_dir()
    WriteJohnCodeToXlsx(data_dir, sheet_manager)
    rt = configManager.get_retention_times()
    analytes = rt.keys()
    pick_peak(rt, sheet_manager, data_dir)
    calc_quant_sheet(sheet_manager)
    sheet_manager.save_workbook()
    calc_quant_full(sheet_manager, analytes)
    sheet_manager.save_workbook()
    calc_external_standards(sheet_manager, analytes)
    sheet_manager.save_workbook()
