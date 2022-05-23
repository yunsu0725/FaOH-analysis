from analysis.join_code import WriteJohnCodeToXlsx
from analysis.file_utils import ConfigManager
from pathlib import Path

from analysis.sheet_manager import SheetManager


if __name__ == '__main__':
    configManager = ConfigManager(Path('./exp.yml'))
    sheet_manager = SheetManager(configManager.get_result_file_path())
    sheet_manager.create()
    WriteJohnCodeToXlsx(configManager.get_data_dir(), sheet_manager)
    # rt = configManager.get_retention_times()
    # print(f'retention_times: {rt}')
    sheet_manager.save_workbook()
