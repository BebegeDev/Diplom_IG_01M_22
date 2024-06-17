import os
import sys
from Utill.create_img import *
from Connected.connection_db import add_user
from TechnicalSpecifications.SolarModule import Sun, SES, Inverter
from Requests.requests_bd import *
import pvlib


def downloading_information_about_sam(sun, a, b, delta_T, STC_min,
                                      STC_max, Technology, Bifacial, V_oc_ref_min, V_oc_ref_max, name_ses):
    name = name_ses
    PV_Modules = pvlib.pvsystem.retrieve_sam(name)
    panel_data = []
    PV_Modules2 = PV_Modules.transpose()
    PV_Modules2 = PV_Modules2.rename_axis('Name').reset_index()
    for i in range(len(PV_Modules2)):
        if STC_min <= PV_Modules2['STC'].iloc[i] <= STC_max:
            if PV_Modules2['Technology'].iloc[i] == Technology:
                if PV_Modules2['Bifacial'].iloc[i] == Bifacial:
                    if V_oc_ref_min <= PV_Modules2['V_oc_ref'].iloc[i] < V_oc_ref_max:
                        name = PV_Modules2['Name'].iloc[i]
                        panel_data.append([name, PV_Modules[name]])
    panels = {}
    for name, ses in panel_data:
        panel = SES(sun, ses, name, a, b, delta_T)
        panels[name] = panel
    return panels


def downloading_information_about_inverter(ses, Paco_min, Paco_max, name_inv, Idcmax, Vac, S):
    name = name_inv
    inverter = pvlib.pvsystem.retrieve_sam(name)
    inverter_data = []
    inverters = []
    inverters_CEC2 = inverter.transpose()
    inverters_CEC2 = inverters_CEC2.rename_axis('Name').reset_index()
    for i in range(len(inverters_CEC2)):
        if inverters_CEC2['Vac'].iloc[i] == Vac:
            if Paco_min < inverters_CEC2['Paco'].iloc[i] < Paco_max:
                if inverters_CEC2['Idcmax'].iloc[i] < Idcmax:
                    name = inverters_CEC2['Name'].iloc[i]
                    inverter_data.append([name, inverter[name]])
    for _, s in ses:
        for name, inv in inverter_data:
            inverter = Inverter(inv, name, s, S)
            inverters.append([name, inverter])
    return inverters


def get_choosing_sam(self):
    return self.__sam


def main_ses(param_ses):
    param_ses = param_ses[0]
    latitude = float(param_ses["Широта"])
    longitude = float(param_ses["Долгота"])
    altitude = float(param_ses["ВнУМ"])
    loc = param_ses["Локация"]
    year_model = int(param_ses["Год моделирования"])
    surface_tilt = int(param_ses["Угол наклона к горизонту"])
    surface_azimuth = int(param_ses["Азимут"])
    albedo = param_ses["Альбедо"]
    name_ses_bd = param_ses["БД ФЭМ"]
    name_inv_bd = param_ses["БД Инверторов"]
    STC_min = float(param_ses["STC min"])
    STC_max = float(param_ses["STC max"])
    Technology = param_ses["Technology"]
    Bifacial = int(param_ses["Bifacial"])
    V_oc_ref_min = float(param_ses["V_oc_ref_min"])
    V_oc_ref_max = float(param_ses["V_oc_ref_max"])
    ka = float(param_ses["ka"])
    kb = float(param_ses["kb"])
    dT = float(param_ses['dT'])
    Vac = param_ses["Vac"]
    Paco_min = float(param_ses["Paco_min"])
    Paco_max = float(param_ses["Paco_max"])
    Idcmax = float(param_ses["Idcmax"])
    S = float(param_ses["Площадь СЭС"])




    with open("resources\\file\\SPP\\report_SPP.html", "w", encoding="utf-8") as f:
        # connect = add_user()
        sun = Sun(latitude, longitude, altitude, loc, year_model, surface_tilt, surface_azimuth, albedo)
        f.write("<html><head><title>Отчет SPP</title></head><body>")
        f.write("<h1>Отчет по расчету</h1>")
        f.write("<h2>Локация</h2>")
        f.write(f"<pre>{sun.get_location_determination()}</pre>")
        f.write("<h2>Период моделирования</h2>")
        f.write(f"<pre>{sun.get_defining_modeling_period()}</pre>")
        f.write("<h2>Определение положения Солнца на небосводе</h2>")
        f.write(f"<pre>{sun.get_determining_position_sun_in_sky()}</pre>")
        sun.get_let_determine_offset_relative_utc()
        f.write("<h2>Изотропная небесная сфера</h2>")
        f.write(f"<pre>{sun.get_calculation_isotropic_celestial_sphere()}</pre>")
        f.write("<h2>Анизотропная небесная сфера</h2>")
        f.write(f"<pre>{sun.get_calculation_anisotropic_celestial_sphere()}</pre>")
        f.write("<h2>Отражённое от воды солнечное излучение</h2>")
        f.write(f"<pre>{sun.get_calculation_solar_radiation_reflected_water()}</pre>")
        f.write("<h2>Месячные суммы суммарной, диффузной и прямой солнечной радиации</h2>")
        f.write(f"<pre>{sun.get_calc_monthly_solar_radiation()}</pre>")
        f.write("<h2>Определение оптимальной ориентации приёмной поверхности</h2>")
        optimal_orientation = sun.determining_optimal_orientation(f)
        f.write(f"<pre>{optimal_orientation}</pre>")
        ses_list = downloading_information_about_sam(sun, ka, kb, dT, STC_min, STC_max, Technology, Bifacial, V_oc_ref_min, V_oc_ref_max, name_ses_bd).items()
        f.write("<h2>Выбор ФЭМ</h2>")
        for name_ses, ses in ses_list:
            f.write(f"<h3>{name_ses}</h3>")
            f.write(f"<pre>{ses.ses}</pre>")
            f.write(f"<pre>Минимальная температура окр.воздуха: {sun.get_let_determine_offset_relative_utc()['temp_air'].min()}</pre>")
            f.write(
                f"<pre>Максимальная температура окр.воздуха: {sun.get_let_determine_offset_relative_utc()['temp_air'].max()}</pre>")
            f.write(
                f"<pre>   Минимальная температура по PVGIS: {round(ses.get_temperature_calculation().min(), 2)}</pre>")
            f.write(
                f"<pre>   Максимальная температура по PVGIS: {round(ses.get_temperature_calculation().max(), 2)}</pre>")
            f.write(
                f"<pre>Расчёт выработки энергии единичным ФЭМ:</pre>")
            f.write(f"<pre>{ses.get_calc_energy_prod_single_fem()}</pre>")
            # create_images_temperature_calculation(ses.get_temperature_calculation(),
            #                                       sun.get_let_determine_offset_relative_utc(), name_ses)
            # create_images_building_vah(ses.get_building_vah(), name_ses)
            # create_images_power_single_diode(ses.get_calc_energy_prod_single_fem(), name_ses)
            # create_images_temperature_calculation(ses.get_temperature_calculation(),
            #                                       sun.get_let_determine_offset_relative_utc(), name_ses)
        inverter_list = downloading_information_about_inverter(ses_list, Paco_min, Paco_max, name_inv_bd, Idcmax, Vac, S)
        f.write("<h2>Выбор Инвертора</h2>")
        for name_inv, inverter in inverter_list:
            f.write(f"<h3>{name_inv} ||| {inverter.ses.name}</h3>")
            f.write(f"<pre>{inverter.inf}</pre>")
            f.write(f"<pre>Максимальное напряжение ХХ ФЭМ, В: {inverter.get_max_voltage_element()}</pre>")
            f.write(f"<pre>Максимальное DC напряжение инвертора, В: {inverter.inf['Vdcmax']}</pre>")
            f.write(f"<pre>К инвертору {name_inv} можно подключить, "
                    f"{inverter.get_calc_number_sequentially_m()}, ФЭМ соединённых последовательно.</pre>")
            f.write(f"<pre>Максимальный ток КЗ ФЭМ, А: {round(inverter.get_max_value_sh_circuit_i(), 2)}</pre>")
            f.write(f"<pre>Максимальный DC ток инвертора: {inverter.inf['Idcmax']}</pre>")
            f.write(f"<pre>Количество параллельно соединённых цепочек ФЭМ: {inverter.get_calc_number_parallel_m()}</pre>")
            f.write(f"<pre>Пиковая мощность единичного ФЭМ, Вт: {inverter.ses.ses['STC']}</pre>")
            f.write(f"<pre>Мощность батареи ФЭМ, подключённой к инвертору, Вт: {round(inverter.get_calculation_peak_battery_power(), 1)}</pre>")
            f.write(f"<pre>Коэффициент загрузки инвертора должен лежать в пределах 0,85...1,25</pre>")
            f.write(f"<pre>Коэффициент загрузки инвертора, о.е.: {inverter.get_load_factor_inverter()}</pre>")
        inverter = max(inverter_list, key=lambda pair: pair[1].get_load_factor_inverter())
        max_inverter_name, max_inverter = inverter
        f.write("<h2>Выбор ФЭМ и инвертора</h2>")
        f.write(f"<pre>Выбираем: инвертор {max_inverter_name} и ФЭМ {max_inverter.ses.name} т.к. его коэффициент ближе к 1 {max_inverter.get_load_factor_inverter()}</pre>")
        f.write(f"<h3>Характеристики ФЭМ</h3>")
        f.write(f"<pre>{max_inverter.ses.ses}</pre>")
        f.write(f"<h3>Характеристики инвертора</h3>")
        f.write(f"<pre>{max_inverter.inf}</pre>")
        f.write(f"<pre>Годовая выработка энергии в сеть, МВтч, {round(max_inverter.get_power_generation_ac().sum() / 1000000, 3)}</pre>")
        f.write(
            f"<pre>Годовая выработка энергии батареей ФЭМ, МВтч, {round(max_inverter.get_calc_power_battery().sum() / 1000000, 3)}</pre>")
        f.write(f"<pre>Коэффициент использования установленной мощности AC, %: {max_inverter.get_utilization_rate_installed_power_ac()}</pre>")
        f.write(f"<pre>Коэффициент использования установленной мощности DC, %: {max_inverter.get_utilization_rate_installed_power_dc()}</pre>")
        f.write(f"<pre>Площадь одного блока: {max_inverter.get_calc_space_ses()}</pre>")
        f.write(f"<pre>Количество модулей в одном блоке: {max_inverter.get_calc_number_parallel_m() +
              max_inverter.get_calc_number_sequentially_m()}</pre>")
        sum_blok = int(max_inverter.get_calc_min_f()/max_inverter.get_calc_space_ses())
        f.write(f"<pre>Количество блоков {sum_blok}</pre>")
        power_one_h = (round(max_inverter.get_power_generation_ac().sum() / 1000000, 3) / 8760)
        # print("Мощность (установленная) СЭС:", (int(max_inverter.get_calc_min_f()/max_inverter.get_calc_space_ses())) *
        #       power_one_h)
        f.write(f"<pre>Годовая выработка энергии СЭС в сеть, МВтч "
                f"{round(sum_blok * max_inverter.get_power_generation_ac().sum() / 1000000, 3)}</pre>")

        # created_images_sum_m_power(monthly_sums)
        # created_images_sum_d_power(daily_sums)
        # created_images_sum_h_power(df_h)
        create_images_temperature_calculation(max_inverter.ses.get_temperature_calculation(),
                                              sun.get_let_determine_offset_relative_utc(), max_inverter.ses.name)
        create_images_building_vah(max_inverter.ses.get_building_vah(), max_inverter.ses.name)
        create_images_power_single_diode(max_inverter.ses.get_calc_energy_prod_single_fem(), max_inverter.ses.name)
        create_images_temperature_calculation(max_inverter.ses.get_temperature_calculation(),
                                              sun.get_let_determine_offset_relative_utc(), max_inverter.ses.name)
        create_images_position_sun_in_sky(sun.get_determining_position_sun_in_sky())
        create_images_DNI_extra(sun.get_determination_solar_radiation_up_boundary_atmosphere())
        create_images_irradiation(sun.get_pvgis_data())
        create_images_isotropic_celestial_sphere(sun.get_pvgis_data(), sun.get_calculation_isotropic_celestial_sphere())
        create_images_anisotropic_celestial_sphere(sun.get_pvgis_data(),
                                                   sun.get_calculation_anisotropic_celestial_sphere(),
                                                   sun.get_calculation_isotropic_celestial_sphere())
        create_images_solar_radiation_reflected_water(sun.get_calculation_solar_radiation_reflected_water())
        create_images_optimization_tilt_angle(optimal_orientation)
        create_images_radiation_during_year(sun.get_calc_monthly_solar_radiation())
        create_images_radiation_inclined_surface(sun.G)

        img_1 = os.path.abspath("resources\\images\\SPP\\Положение Солнца на небосводе.png")
        img_2 = os.path.abspath("resources\\images\\SPP\\Заатмосферная солнечная радиация.png")
        img_3 = os.path.abspath("resources\\images\\SPP\\Cолнечное излучение, падающее на горизонтальную поверхность.png")
        img_4 = os.path.abspath("resources\\images\\SPP\\Диффузное солнечное излучение, падающее на наклонную поверхность (изотропное).png")
        img_5 = os.path.abspath("resources\\images\\SPP\\Диффузное солнечное излучение, падающее на наклонную поверхность (анизотропное).png")
        img_6 = os.path.abspath("resources\\images\\SPP\\Диффузное солнечное излучение (отражённое от воды), падающее на наклонную поверхность.png")
        img_7 = os.path.abspath("resources\\images\\SPP\\Угол установки приёмной поверхности.png")
        img_8 = os.path.abspath("resources\\images\\SPP\\Солнечное излучение, падающее на наклонную поверхность_2.png")
        img_9 = os.path.abspath("resources\\images\\SPP\\Месячные суммы суммарного солнечного излучения.png")
        img_10 = os.path.abspath(f"resources\\images\\SPP\\Температура ФЭМ ({max_inverter.ses.name}).png")
        img_11 = os.path.abspath(f'resources\\images\\SPP\\ВАХ ({max_inverter.ses.name}).png')
        img_12 = os.path.abspath(f'resources\\images\\SPP\\Мощность единичного ФЭМ ({max_inverter.ses.name}).png')

        f.write("<h2>Графики</h2>")

        img_list = [
            [img_1, "Положение Солнца на небосводе"],
            [img_2, "Заатмосферная солнечная радиация"],
            [img_3, "Cолнечное излучение, падающее на горизонтальную поверхность"],
            [img_4, "Диффузное солнечное излучение, падающее на наклонную поверхность (изотропное)"],
            [img_5, "Диффузное солнечное излучение, падающее на наклонную поверхность (анизотропное)"],
            [img_6, "Диффузное солнечное излучение (отражённое от воды), падающее на наклонную поверхность"],
            [img_7, "Угол установки приёмной поверхности"],
            [img_8, "Солнечное излучение, падающее на наклонную поверхность_2"],
            [img_9, "Месячные суммы суммарного солнечного излучения"],
            [img_10, f"Температура ФЭМ ({max_inverter.ses.name})"],
            [img_11, f"resources\\images\\SPP\\ВАХ ({max_inverter.ses.name})"],
            [img_12, f"Мощность единичного ФЭМ ({max_inverter.ses.name})"]
        ]
        for img, name in img_list:
            f.write(f"<h3>{name}</h3>")
            f.write('<div class="image-container">')
            f.write(f'<img src="{img}" alt="{name}">')
            f.write('</div>')


        return max_inverter.get_power_generation_ac() / 1000 * sum_blok, max_inverter.ses.name, max_inverter_name


if __name__ == '__main__':
    connect = add_user()
    a, b, delta_T = get_param_operator_ses(connect, "k_a, k_b, d_T")
    latitude, longitude, altitude, loc, year_model, surface_tilt, surface_azimuth, albedo, name_ses, name_inv, S = (
        get_param_operator_ses(connect, "Широта, "
                                        "Долгота, "
                                        "ВнУМ, "
                                        "Локация, "
                                        "Год_моделирования, "
                                        "Угол_наклона_к_горизонту,"
                                        "Азимут,"
                                        "Альбедо,"
                                        "БД_ФЭМ,"
                                        "БД_Инверторов,"
                                        "Площадь_СЭС"))
    param_ses = [
        {
            "Локация": loc,
            "Широта": latitude,
            "Долгота": longitude,
            "ВнУМ": altitude,
            "Год моделирования": year_model,
            "Угол наклона к горизонту": surface_tilt,
            "Азимут": surface_azimuth,
            "Альбедо": albedo,
            "БД ФЭМ": name_ses,
            "STC min": 400,
            "STC max": 405,
            "Technology": "Mono-c-Si",
            "Bifacial": 0,
            "V_oc_ref_min": 40,
            "V_oc_ref_max": 400,
            "ka": a,
            "kb": b,
            "dT":delta_T,
            "БД Инверторов": name_inv,
            "Vac": '240',
            "Paco_min": 11000,
            "Paco_max": 12000,
            "Idcmax": 24,
            "Площадь СЭС": S
        }
    ]
    power_ses = main_ses(param_ses)
