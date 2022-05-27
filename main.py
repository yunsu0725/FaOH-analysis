from analysis.raw_data_parser import process_raw_data, parse_data_points_from_raw_txt
from analysis.peak import calc_quant_full, calc_quant_sheet, pick_peak_from_data_points, pick_peak
from analysis.utils import ConfigManager, get_all_txt_files, get_vial_names
from analysis.external_data import calc_external_standards, calc_external_std_data_from_dp
from analysis.sheet_manager import SheetManager
from analysis.concentrate import calc_and_concentrate_data
from pathlib import Path
import click


welcome_msg = "This is an interactive command line tool for processing your experiment data. Let's do it step by step!"

init_msg = """
There are two things you need to do before using this tool:
1. Wrap your txt files in a folder
2. Put that folder under the "data" directory.
3. Open "exp.yml" (it should be in the same folder as "main.py") and enter the following information for further data processing.
    a) data_dir: The name of the folder you put your txt files in.
    b) target_file: Name you want for your final excel file.
"""

confirm_yaml_update_msg = "Have you updated the 'data_dir' and 'target_file' in the YAML config?"

preprocess_end_description = """
The program finishes the raw data processing. Now you should see the target .xlsx file under res/ directory.
There's a sheet 'Preprocessed Data' listing what from the .txt files.
Now you might want to read the sheet and check the new 'retention_time' values, so the program will pause until you finish.
"""

confirm_r_time_description = "Have you updated the 'retention_time' in the YAML config?"

quant_sheet_end_description = """
Now you can see that there's another sheet with the quantification data. There might be some missing peaks, and the
program will pause until you manually updating them.
"""

confirm_quant_description = "Have you updated the missing peaks in the quantification sheet, if any?"


@click.command()
def new_flow():
    print(welcome_msg)
    print(init_msg)
    if not click.confirm(confirm_yaml_update_msg, default=True):
        exit()

    configManager = ConfigManager(Path('./exp.yml'))
    sheet_manager = SheetManager(configManager.get_result_file_path())
    sheet_manager.create()
    data_dir = configManager.get_data_dir()
    all_txt_files = get_all_txt_files(data_dir)
    vial_names = get_vial_names(all_txt_files)
    process_raw_data(data_dir, sheet_manager)
    data_points = parse_data_points_from_raw_txt(data_dir)
    sheet_manager.write_raw_data_points(data_points, vial_names)
    sheet_manager.save_workbook()

    print(preprocess_end_description)
    if not click.confirm(confirm_r_time_description, default=True):
        exit()

    print("The program is processing the quantification sheet.")
    rt = configManager.get_retention_times()
    analytes = rt.keys()
    peak_dp = pick_peak_from_data_points(data_points, rt, analytes, vial_names)
    sheet_manager.write_quantification_sheet(peak_dp, vial_names, analytes)
    sheet_manager.save_workbook()
    print(quant_sheet_end_description)

    # Now it's researcher's turn to add those missing peaks manually
    # There's such a condition because the variance of the tolerance threshold
    # Since it is intuitive to modify the sheet directly,
    # we'll update the datapoints after the researcher finishes updating the quant sheet

    if not click.confirm(confirm_quant_description, default=True):
        exit()

    dp = sheet_manager.load_data_points_from_quant_sheet(vial_names)
    x, conc_num = calc_external_std_data_from_dp(
        dp, alc_acid_id='FaOH', analytes=analytes)
    sheet_manager.write_ext_std_sheet(x, conc_num)
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
