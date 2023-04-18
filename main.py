from analysis.raw_data_parser import parse_data_points_from_raw_txt
from analysis.peak import pick_peaks
from analysis.utils import ConfigManager, get_all_txt_files, get_vial_names
from analysis.external_data import calc_external_std_data
from analysis.sheet_manager import SheetManager
from analysis.concentrate import calc_and_concentrate_data
from pathlib import Path
import click


welcome_msg = "This is an interactive command line tool for processing your experiment data. Let's do it step by step!"

preprocess_end_description = """
The program finishes the raw data processing.
You should find two files, miao.xlsx and config.yml, in the folder.
The config.yml is where you might need to update, and the miao.xlsx is the result.
There's a sheet 'Preprocessed Data' listing what from the .txt files.

You should check the sheet and update the 'retention_time' values in the YAML file.
Also, you can change the peak threshold as you want by updating 'peak_threshold' value in the YAML.
"""

confirm_r_time_description = "Have you updated the YAML config?"

quant_sheet_end_description = """
Now you can find another sheet with the quantification data.
There might be some missing peaks, please check and update them manually.
"""

confirm_quant_description = "Have you updated the missing peaks in the quantification sheet, if any?"


@click.command()
@click.option('--data_dir', prompt='Please paste the target data directory')
def process(data_dir: str):
    configManager = ConfigManager(Path(data_dir))
    sheet_manager = SheetManager(configManager.get_result_file_path())
    sheet_manager.create()
    data_dir = configManager.get_data_dir()
    all_txt_files = get_all_txt_files(data_dir)
    vial_names = get_vial_names(all_txt_files)
    data_points = parse_data_points_from_raw_txt(data_dir)
    sheet_manager.write_raw_data_points(data_points, vial_names)
    sheet_manager.save_workbook()

    print(preprocess_end_description)
    if not click.confirm(confirm_r_time_description, default=True):
        exit()

    rt = configManager.get_retention_times()
    analytes = rt.keys()
    peak_threshold = configManager.get_peak_threshold()
    peak_dp = pick_peaks(data_points, rt, analytes, vial_names, peak_threshold)
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
    x, conc_num = calc_external_std_data(
        dp, alc_acid_id='FaOH', analytes=analytes)
    sheet_manager.write_ext_std_sheet(x, conc_num)
    sheet_manager.save_workbook()
    int_std_conc = configManager.get_internal_std_conc()
    calc_and_concentrate_data(sheet_manager, int_std_conc)


if __name__ == '__main__':
    process()
