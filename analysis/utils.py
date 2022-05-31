import os
import re
from pathlib import Path
import io
import yaml


def get_main_dir():
    return Path('.')


def get_area_from_row(r):
    return r[3]


def get_peak_id_from_row(r):
    return r[5]


class ConfigManager:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.config_path = data_dir / 'config.yml'
        if not self.config_path.exists():
            self._create_config_file()

    def _create_config_file(self):
        with open(self.config_path, 'w') as f:
            template = {
                'retention_time': {
                    f'C{idx}': 0 for idx in range(3, 19)
                    # C3: 0, C4: 0,..., C18: 0
                },
                'internal_std_conc': {
                    f'C{idx}': 50 for idx in range(3, 19, 2)
                    # C3: 50, C5: 50,..., C17: 50
                }
            }
            yaml.dump(template, f, default_flow_style=False, sort_keys=False)

    def _get_config(self, key: str):
        with io.open(self.config_path, 'r') as f:
            configs = yaml.safe_load(f)
            try:
                res = configs[key]
                return res
            except KeyError:
                print(f'please specify key: {key} in the yaml file.')
            return None

    def get_data_dir(self) -> Path:
        exp_data_dir = self._get_config('data_dir')
        if exp_data_dir is None:
            return None
        return Path(exp_data_dir)

    def get_result_file_path(self) -> Path:
        target_file = self._get_config('target_file')
        data_dir = self.get_data_dir()
        if target_file is None or data_dir is None:
            return None
        return data_dir / target_file

    def get_retention_times(self):
        return self._get_config('retention_times')

    def get_internal_std_conc(self):
        return self._get_config('internal_std_conc')


def get_all_txt_files(data_dir: Path):
    all_files = os.listdir(data_dir)
    txt_files = [x for x in all_files if re.match(r'.*\.TXT', x)]
    return txt_files


def get_vial_names(all_txt_files):
    return [x[:-4] for x in all_txt_files]
