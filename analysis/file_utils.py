import os
import re

def get_all_txt_files(target_dir):
    all_files = os.listdir(target_dir)
    txt_files = [x for x in all_files if re.match(r'.*\.txt', x)]
    return txt_files