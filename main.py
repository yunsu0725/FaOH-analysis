from ast import Load
from json import load
import yaml
import io
from analysis.join_code import WriteJohnCodeToXlsx
from pathlib import Path

pwd = Path('.')

def get_res_dir():
    return pwd / 'res'
    
def get_data_dir():
    return pwd / 'data'

def load_configs():
    with io.open('exp.yml', 'r') as f:
        data_loaded = yaml.safe_load(f)
    return data_loaded
    

if __name__ == '__main__':
    configs = load_configs()
    print(f'configs: {configs}')
    try:
        target_file_name = configs['target_file']
        # data_dir = configs['data_dir']
        data_dir = get_data_dir()
        target_file_path = get_res_dir() / target_file_name
        WriteJohnCodeToXlsx(data_dir, target_file_path)
    except KeyError as e:
        print(f'fail to get key: {e}')
        