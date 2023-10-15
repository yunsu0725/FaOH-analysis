from analysis.raw_data_parser import parse_data_points_from_raw_txt
from analysis.peak import pick_peaks
from analysis.utils import ConfigManager, get_all_txt_files, get_vial_names
from analysis.external_data import calc_external_std_data
from analysis.sheet_manager import SheetManager
from analysis.concentrate import calc_and_concentrate_data
from pathlib import Path
import click


welcome_msg = "This is an interactive command line tool to convert peak area into product concentrations. Let's get started!"

preprocess_end_description = """
The program had extracted RT and peak area data from .txt files into a large Excel sheet named GCFID.xlsx. 
Under the same folder there's another new file named config.yml. Update RT and internal std concentrations in this file by referring to the "Preprocessed Data" tab of GCFID.xlsx.
Save the .yml file and answer the question below.
"""

confirm_r_time_description = "Have you updated RT and int. std. in config.yml?"

quant_sheet_end_description = """
Now you can find another tab in GCFID.xlsx named "Quantification with IS, ES".
If you don't see any values in the tab, reopen the Excel sheet.
If there are missing peaks, check and update them manually from "Preprocessed Data" tab.
"""

confirm_quant_description = """Have you updated the missing peaks in the "Quantification" tab, if any?"""


@click.command()
@click.option('--data_dir', prompt='Please paste the path of your target data folder')
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

    concentrate_data = calc_and_concentrate_data(sheet_manager, int_std_conc)
    sheet = sheet_manager.load_concentration_sheet()
    for d in concentrate_data:
        sheet.append(d)
    sheet_manager.save_workbook()


if __name__ == '__main__':
    process()
