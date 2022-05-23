from analysis.join_code import WriteJohnCodeToXlsx
from analysis.peak import pick_peak
from analysis.file_utils import ConfigManager
from pathlib import Path

from analysis.sheet_manager import SheetManager


if __name__ == '__main__':
    configManager = ConfigManager(Path('./exp.yml'))
    sheet_manager = SheetManager(configManager.get_result_file_path())
    sheet_manager.create()
    data_dir = configManager.get_data_dir()
    WriteJohnCodeToXlsx(data_dir, sheet_manager)
    rt = configManager.get_retention_times()
    print(f'{rt=}')
    pick_peak(rt, sheet_manager, data_dir)
    sheet_manager.save_workbook()
