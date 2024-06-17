import os
import glob
import csv
from main_HPS2 import main_ges
from main_SES import main_ses
from Utill.create_img import *
import Utill.calc as calc


def main_ges_ses(ges, ses, load):
    with open("resources\\file\\HPS_SPP\\report_HPS_SPP.html", "w", encoding="utf-8") as f:
        f.write("<html><head><title>Отчет HPS</title></head><body>")
        f.write("<h1>Отчет по расчету</h1>")
        load = list(load[0].values())
        load = list(map(float, load))

        q, zf, param_hps = ges
        param_spp = ses
        load = load * 365
        main_ges(q, zf, param_hps)
        power_ses, name_ses, name_inv = main_ses(param_spp)
        folder_path = 'resources/file/HPS/'
        file_pattern = 'ГЭС * кол-во ГА *.csv'
        matching_files = glob.glob(folder_path + file_pattern)

        for file_path in matching_files:
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            f.write(f"<h2>Расчет для {file_name} ||| ФЭМ {name_ses} ||| Инвертора {name_inv}</h2>")
            power_ges = []
            with open(file_path, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    for value in row:
                        power_ges.append(float(value.strip()))

            df_h, df_md = calc.create_sum_year_h_power(power_ses, load, power_ges)

            monthly_sums = [calc.create_sum_year_m_power(df, col) for df, col in df_md]

            daily_sums = [calc.create_sum_year_d_power(df, col) for df, col in df_md]

            str_file = f"{file_name}_{name_ses}_{name_inv} M"
            created_images_sum_m_power(monthly_sums, str_file)
            img = os.path.abspath(f"resources/images/HPS_SPP/{str_file}.png")
            f.write("<h3>Месячный график выработки и нагрузки</h3>")
            f.write('<div class="image-container">')
            f.write(f'<img src="{img}">')
            f.write('</div>')

            str_file = f"{file_name}_{name_ses}_{name_inv} D"
            created_images_sum_d_power(daily_sums, str_file)
            img = os.path.abspath(f"resources/images/HPS_SPP/{str_file}.png")
            f.write("<h3>Дневной график выработки и нагрузки</h3>")
            f.write('<div class="image-container">')
            f.write(f'<img src="{img}">')
            f.write('</div>')

            str_file = f"{file_name}_{name_ses}_{name_inv} H"
            created_images_sum_h_power(df_h, str_file)
            img = os.path.abspath(f"resources/images/HPS_SPP/{str_file}.png")
            f.write("<h3>Почасовой график выработки и нагрузки</h3>")
            f.write('<div class="image-container">')
            f.write(f'<img src="{img}">')
            f.write('</div>')



        print("END")





    # u = c.Util()
    # load = u.open_csv('load.csv', 'r')[0]
    # name_ges = input("Выбирите вариант ГЭС: ")
    # power_ges = u.open_csv(f'ges_{name_ges}_hourly_energy_output.csv', 'r')[0]
    # power_ses_h = power_ses
    # df_h, df_md = calc.create_sum_year_h_power(power_ses_h, load, power_ges)
    # monthly_sums = [calc.create_sum_year_m_power(df, col) for df, col in df_md]
    # daily_sums = [calc.create_sum_year_d_power(df, col) for df, col in df_md]
    # created_images_sum_m_power(monthly_sums)
    # created_images_sum_d_power(daily_sums)
    # created_images_sum_h_power(df_h)