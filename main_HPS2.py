import os
from Connected.connection_db import add_user
from TechnicalSpecifications.HPS2 import SmallHPS, SecurityCurves
import Utill.calc as c
from Requests.requests_bd import *
from Utill.create_img import *


def main_ges(q, zf, param_hps):
    param_hps = param_hps[0]
    with open("resources\\file\\HPS\\report_HPS.html", "w", encoding="utf-8") as f:
        npu, absolute_mark, summ = float(param_hps['НПУ']), float(param_hps['УНБ']), param_hps['Весенне-летний_период']
        wint, ny, k = param_hps['Осенне–зимний_период'], float(param_hps['КПД']), float(param_hps['k_N'])
        connect = add_user()
        hps = SmallHPS()
        sco = SecurityCurves(50)
        sct = SecurityCurves(90)
        hps.calc_security_curves(q)
        hps.calc_z_v_f(zf)
        hps.q_min_q_max()
        hps.calc_summ_wint_q()
        hps.calc_summ_wint_z(absolute_mark)


        f.write("<html><head><title>Отчет HPS</title></head><body>")
        f.write("<h1>Отчет по расчету</h1>")
        f.write("<h2>Гидрологический ряд расходов воды</h2>")

        f.write(f"<pre>{hps.yearly_averages}</pre>")

        sco.calc_conversion_factors(hps.yearly_averages)
        sco.calc_avg_monthly_year()
        f.write('<hr>')
        sco.calc_annual_runoff(summ, wint, q)

        f.write("<h2>Расчетные значения обеспеченности для выбора маловодного и средневодного года</h2>")
        f.write(
            f"<p>Ближайший год слева от {sco.percent}%: {sco.left['Годы_ср_г']}, P = {sco.left['P,%']}%, Qrt = {round(sco.left['Qrt'], 2)}</p>")
        f.write(
            f"<p>Ближайший год справа от {sco.percent}%: {sco.right['Годы_ср_г']}, P = {sco.right['P,%']}%, Qrt = {round(sco.right['Qrt'], 2)}</p>")

        sct.calc_conversion_factors(hps.yearly_averages)
        sct.calc_avg_monthly_year()
        sct.calc_annual_runoff(summ, wint, q)

        f.write(f'<p>Для года {sco.year_one} коэффициент в межень {round(sco.km_one, 2)}</p>')
        f.write(f'<p>Для года {sco.year_one} коэффициент в половодье {round(sco.kp_one, 2)}</p>')
        f.write(f'<p>Для года {sco.year_two} коэффициент в межень {round(sco.km_two, 2)}</p>')
        f.write(f'<p>Для года {sco.year_two} коэффициент в половодье {round(sco.kp_two, 2)}</p>')
        f.write(f"<p>В качестве расчетного средневодного года принимаем {sco.result}</p>")

        f.write('<hr>')
        f.write(
            f"<p>Ближайший год слева от {sct.percent}%: {sct.left['Годы_ср_г']}, P = {round(sct.left['P,%'], 2)}%, Qrt = {round(sct.left['Qrt'], 2)}</p>")
        f.write(
            f"<p>Ближайший год справа от {sct.percent}%: {sct.right['Годы_ср_г']}, P = {round(sct.right['P,%'], 2)}%, Qrt = {round(sct.right['Qrt'], 2)}</p>")
        f.write(f'<p>Для года {sct.year_one} коэффициент в межень {round(sct.km_one, 2)}</p>')
        f.write(f'<p>Для года {sct.year_one} коэффициент в половодье {round(sct.kp_one, 2)}</p>')
        f.write(f'<p>Для года {sct.year_two} коэффициент в межень {round(sct.km_two, 2)}</p>')
        f.write(f'<p>Для года {sct.year_two} коэффициент в половодье {round(sct.kp_two, 2)}</p>')
        f.write(f"<p>В качестве расчетного маловодного года принимаем {sct.result}</p>")
        f.write('<hr>')
        f.write("<h2>Годовой сток</h2>")
        f.write(
            "<p>Выбрав окончательно расчетные гидрографы средневодного и маловодного годов, необходимо уточнить годовой сток.</p>")
        f.write(f"<p>Расчетный маловодный год {sct.year} (P% = {sct.percent}) с приведением.</p>")
        f.write(f"<pre>{sct.spring_summer_period}</pre>")
        f.write(f"<pre>{sct.autumn_winter_period}</pre>")
        f.write(f"<p>Расчетный маловодный год % без приведения.</p>")
        f.write(f"<pre>{sct.row}</pre>")
        f.write(f"<p>Расчетный средневодный год {sco.year} (P% = {sco.percent}) с приведением.</p>")
        f.write(f"<pre>{sco.spring_summer_period}</pre>")
        f.write(f"<pre>{sco.autumn_winter_period}</pre>")
        f.write(f"<p>Расчетный средневодный год {sco.year} без приведения.</p>")
        f.write(f"<pre>{sco.row}</pre>")
        f.write("<h2>Корректировка</h2>")
        pol = c.adjustment_annual_runoff(df_low=sct.spring_summer_period, df_medium=sco.spring_summer_period,
                                         period="половодье", f=f)
        f.write('<hr>')
        mej = c.adjustment_annual_runoff(df_low=sct.autumn_winter_period, df_medium=sco.autumn_winter_period,
                                         period="межень", f=f)
        f.write('<hr>')

        sct.calc_h_pod(pol, mej, hps.q_summ, hps.q_wint, hps.z_summ, hps.z_wint)
        sct.calc_supplied_pressure(npu)
        f.write("<h2>Подведенный напор</h2>")
        for m, data in sct.result.items():
            f.write(f"<pre>{m}: {data}</pre>")
        f.write("<p>Для выбранного расчетного маловодного года и принятой обеспеченности вычисляется значение мощности на бытовом стоке для каждого месяца года:</p>")
        sct.calc_power(k, f)
        hps.calc_h(npu, absolute_mark)
        hps.calculate_total_average(q)
        min_power, max_power, min_h, max_h, min_q, max_q = sct.get_power_h_q_max_min()
        GAs = get_models_hps(connect, min_h, max_h, min_q)
        data_power_ag = hps.checking_work_GA(GAs, sct.power, k, min_q, f)
        f.write("<h2>Новые значения мощности на бытовом стоке для каждого месяца года:</h2>")
        hps.print_new_power(f)

        for i, data in enumerate(hps.data_list):
            list_n_ag = [1,2,3] * len(hps.data_list)
            c.calc_energy_hps(hps.name_list_ga[i], data[1])
            c.calc_hourly_power_consumption(list_n_ag[i], hps.name_list_ga[i], data[1])
        create_images_line_s_w(hps.q_summ, hps.q_wint, hps.z_summ, hps.z_wint)
        created_images_security_curves(hps.yearly_averages)
        created_images_h_pod(sct.get_h_pod_s(), 'Лето')
        created_images_h_pod(sct.get_h_pod_w(), 'Зима')
        create_images_line(hps.v_list, hps.z_list, hps.f_list)
        # Ваша функция для создания HTML

        img_1 = os.path.abspath("resources/images/HPS/Кривые зависимостей расходов воды в створе ГЭС.png")
        img_5 = os.path.abspath("resources/images/HPS/z_f_v.png")
        img_2 = os.path.abspath("resources/images/HPS/Эмпирические кривые обеспеченности.png")
        img_3 = os.path.abspath("resources/images/HPS/Зависимость отметок уровня воды от расхода Зима.png")
        img_4 = os.path.abspath("resources/images/HPS/Зависимость отметок уровня воды от расхода Лето.png")

        f.write("<h2>Графики</h2>")

        f.write("<h3>Кривая зависимости площадей водохранилища от уровня воды в нем</h3>")
        f.write('<div class="image-container">')
        f.write(f'<img src="{img_5}" alt="Кривая зависимости площадей водохранилища от уровня воды в нем">')
        f.write('</div>')

        f.write("<h3>Летний и зимний расходы</h3>")
        f.write('<div class="image-container">')
        f.write(f'<img src="{img_1}" alt="Летний и зимний расходы">')
        f.write('</div>')

        f.write("<h3>Кривые обеспеченности</h3>")
        f.write('<div class="image-container">')
        f.write(f'<img src="{img_2}" alt="Кривые обеспеченности">')
        f.write('</div>')

        f.write("<h3>Зависимость отметок уровня воды от расхода (зима)</h3>")
        f.write('<div class="image-container">')
        f.write(f'<img src="{img_3}" alt="Отметки Z (Зима)">')
        f.write('</div>')

        f.write("<h3>Зависимость отметок уровня воды от расхода (лето)</h3>")
        f.write('<div class="image-container">')
        f.write(f'<img src="{img_4}" alt="Отметки Z (Лето)">')
        f.write('</div>')


if __name__ == '__main__':
    connect = add_user()
    q = c.open_exel('q.xlsx')
    npu, absolute_mark, summ, wint, ny, k = get_param_operator(connect, "НПУ, "
                                                                        "Абсолютная, "
                                                                        "Весенне–летний_период, "
                                                                        "Осенне–зимний_период, "
                                                                        "КПД, "
                                                                        "k_N")
    z, f, _ = get_cur(connect, 'Кривые_F_V_Z', 'Z, F, V')
    param_hps = [
        {'УНБ': absolute_mark, 'НПУ': npu, 'КПД': ny,
         'Весенне-летний_период': summ, 'Осенне–зимний_период': wint, 'k_N': k
         }
    ]
    df = pd.DataFrame(z, f, columns=['z', 'f'])
    main_ges(q, param_hps, df)
