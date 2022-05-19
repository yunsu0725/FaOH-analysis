from analysis.join_code import WriteJohnCodeToXlsx
from analysis.file_utils import ConfigManager
from pathlib import Path

from analysis.sheet_manager import SheetManager


if __name__ == '__main__':
    configManager = ConfigManager(Path('./exp.yml'))
    # WriteJohnCodeToXlsx(configManager.get_data_dir(), configManager.get_result_file_path())
    rt = configManager.get_retention_times()
    print(f'retention_times: {rt}')
