import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def created_images_sum_h_power(df, name):
    data_combined = pd.concat(df, axis=1)
    plt.figure(figsize=(6.4, 4.8))
    for col in data_combined.columns:
        plt.plot(data_combined.index, data_combined[col], label=col)
    plt.xlabel('Time, ч')
    plt.ylabel('Power, кВт')
    plt.title('Почасовой график выработки и нагрузки')
    plt.legend(title='Легенда')
    plt.axhline(y=0, color='k')
    plt.savefig(f'resources\\images\\HPS_SPP\\{name}.png')
    plt.close()


def created_images_sum_m_power(df, name):
    data_combined = pd.concat(df, axis=1)
    plt.figure(figsize=(6.4, 4.8))
    for col in data_combined.columns:
        plt.plot(data_combined.index, data_combined[col], label=col)
    plt.xlabel('Time, м')
    plt.ylabel('Power, МВт')
    plt.title('Месячный график выработки и нагрузки')
    plt.legend(title='Легенда')
    plt.axhline(y=0, color='k')
    plt.savefig(f'resources\\images\\HPS_SPP\\{name}.png')
    plt.close()


def created_images_sum_d_power(df, name):
    data_combined = pd.concat(df, axis=1)
    plt.figure(figsize=(6.4, 4.8))
    for col in data_combined.columns:
        plt.plot(data_combined.index, data_combined[col], label=col)
    plt.xlabel('Time, д')
    plt.ylabel('Power, кВт')
    plt.title('Дневной график выработки и нагрузки')
    plt.legend(title='Легенда')
    plt.axhline(y=0, color='k')
    plt.savefig(f'resources\\images\\HPS_SPP\\{name}.png')
    plt.close()


def create_images_bar(load):
    df = pd.DataFrame(columns=['load'])
    df['load'] = load
    df['load'].plot(figsize=(6.4, 4.8), label='Нагрузка')
    plt.legend()
    plt.grid(linestyle='--')
    plt.ylabel('Мощность, Вт')
    plt.xlabel('Номер часа в году')
    plt.title('Почасовая нагрузка за год')
    plt.savefig('resources\\images\\HPS_SPP\\Почасовая нагрузка за год.png')
    plt.clf()

def create_images_line(v, z, f):
    fig, ax1 = plt.subplots()
    fig.suptitle('Кривая зависимости объемов водохранилища от уровня воды в нем')

    color = 'tab:blue'
    ax1.set_xlabel('v')
    ax1.set_ylabel('Z, м', color=color)
    ax1.plot(v, z, color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twiny()
    color = 'tab:red'
    ax2.set_xlabel('f', color=color)
    ax2.plot(f, z, color=color)
    ax2.tick_params(axis='x', labelcolor=color)

    fig.tight_layout()
    plt.savefig('resources\\images\\HPS\\z_f_v.png')
    plt.clf()

def create_images_line_s_w(q_s, q_w, z_s, z_w):

    # Создание графика
    fig, ax1 = plt.subplots()
    # fig.suptitle('Кривые зависимостей расходов воды в створе ГЭС')

    # Построение кривой для летнего периода
    color_s = 'tab:blue'
    ax1.set_xlabel('Весенне–летний период, м$^3$', color=color_s)
    ax1.set_ylabel('Z, м', color=color_s)
    ax1.plot(q_s, z_s, color=color_s, label='Лето')
    ax1.tick_params(axis='y', labelcolor=color_s)

    # Создание второго графика на том же полотне для зимнего периода
    ax2 = ax1.twiny()
    color_w = 'tab:red'
    ax2.set_xlabel('Осенне–зимний период, м$^3$', color=color_w)
    ax2.plot(q_w, z_w, color=color_w, label='Зима')
    ax2.tick_params(axis='x', labelcolor=color_w)

    # Легенда для графиков
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    # Улучшение оформления
    fig.tight_layout()
    plt.savefig('resources\\images\\HPS\\Кривые зависимостей расходов воды в створе ГЭС.png')
    # plt.show()
    plt.close(fig)


def created_images_security_curves(data):
    df = pd.DataFrame(data)

    max_y = df[['Qrt', 'Qпi', 'Qмi']].max().max() + 10

    plt.figure(figsize=(6.4, 4.8))

    plt.plot(df['P,%'], df['Qrt'], 'o--', label='Qср')
    plt.plot(df['P,%'], df['Qпi'], 'o--', label='Qпi')
    plt.plot(df['P,%'], df['Qмi'], 'o--', label='Qмi')

    for i in range(len(df)):
        plt.text(df['P,%'][i], df['Qrt'][i], str(df['Годы_ср_г'][i]), fontsize=7, ha='right')
        plt.text(df['P,%'][i], df['Qпi'][i], str(df['Годы_п'][i]), fontsize=7, ha='right')
        plt.text(df['P,%'][i], df['Qмi'][i], str(df['Годы_м'][i]), fontsize=7, ha='right')

    # Настройка осей
    plt.xlim(0, 100)
    plt.ylim(0, max_y)

    plt.xlabel('P,%')
    plt.ylabel('Qср, м³/с')
    # plt.title('Кривые обеспеченности')

    plt.legend()

    plt.grid(True)
    plt.savefig('resources\\images\\HPS\\Эмпирические кривые обеспеченности.png')
    # plt.show()
    plt.clf()

def create_images_position_sun_in_sky(SPA):
    SPA['azimuth'].plot(label='Азимутальный угол Солнца', figsize=(6.4, 4.8))
    SPA['elevation'].plot(label='Высота Солнца над горизонтом')
    plt.grid(linestyle='--')
    plt.legend()
    plt.ylabel('Положение Солнца, град.')
    plt.xlabel('Время')
    # plt.title('Положение Солнца на небосводе')
    # plt.show()
    plt.savefig(f'resources\\images\\SPP\\Положение Солнца на небосводе.png')
    plt.clf()


def create_images_DNI_extra(DNI_extra):
    DNI_extra.plot(label='Метод "spenser"', figsize=(6.4, 4.8))
    plt.grid(linestyle='--')
    plt.legend()
    plt.ylabel('СИ на верхней границе атмосферы, Вт/кв.м')
    plt.xlabel('Время')
    # plt.title('Заатмосферная солнечная радиация')
    # plt.show()
    plt.savefig(f'resources\\images\\SPP\\Заатмосферная солнечная радиация.png')
    plt.clf()

def create_images_irradiation(PVGIS_data):
    PVGIS_data['poa_direct'].plot(label='Direct irradiation', figsize=(6.4, 4.8))
    PVGIS_data['poa_sky_diffuse'].plot(label='Diffuse irradiation')
    # PVGIS_data['poa_ground_diffuse'].plot(label='Groud diffuse irradiation')
    plt.legend()
    plt.grid(linestyle='--')
    plt.ylabel('Солнечное излучение, Вт/кв.м')
    plt.xlabel('Время')
    # plt.title('Cолнечное излучение, падающее на горизонтальную поверхность (источник - PVGIS)')
    # plt.show()
    plt.savefig(f'resources\\images\\SPP\\Cолнечное излучение, падающее на горизонтальную поверхность.png')
    plt.clf()


def create_images_isotropic_celestial_sphere(PVGIS_data, diffuse_sky_isotropic):
    PVGIS_data['poa_direct'].plot(label='Direct irradiation', figsize=(6.4, 4.8))
    PVGIS_data['poa_sky_diffuse'].plot(label='Diffuse irradiation')
    diffuse_sky_isotropic.plot(label='Isotropic sky diffuse irradiation', linestyle='--')
    plt.legend()
    plt.grid(linestyle='--')
    plt.ylabel('Солнечное излучение, Вт/кв.м')
    plt.xlabel('Время')
    # plt.title('Сравнение изотропной модели рассеяния и результатов PVGIS')
    # plt.show()
    plt.savefig(f'resources\\images\\SPP\\Сравнение изотропной модели рассеяния и результатов PVGIS.png')
    plt.clf()


def create_images_anisotropic_celestial_sphere(PVGIS_data, diffuse_sky_perez, diffuse_sky_isotropic):
    PVGIS_data['poa_sky_diffuse'].plot(figsize=(6.4, 4.8), label='Горизонтальное СИ')
    diffuse_sky_perez.plot(label='Perez')
    diffuse_sky_isotropic.plot(label='Анизотропное СИ')
    plt.legend()
    plt.grid(linestyle='--')
    plt.ylabel('Солнечное излучение, Вт/кв.м')
    plt.xlabel('Номер часа в году')
    # plt.title('Диффузное солнечное излучение, падающее на наклонную поверхность')
    # plt.show()
    plt.savefig(f'resources\\images\\SPP\\Диффузное солнечное излучение, падающее на наклонную поверхность (анизотропное).png')
    plt.clf()

def create_images_solar_radiation_reflected_water(diffuse_water):
    diffuse_water.plot(figsize=(6.4, 4.8), label='Диффузное СИ отраженное от воды')
    plt.legend()
    plt.grid(linestyle='--')
    plt.ylabel('Солнечное излучение, Вт/кв.м')
    plt.xlabel('Номер часа в году')
    # plt.title('Диффузное солнечное излучение (отражённое от воды), падающее на наклонную поверхность')
    # plt.show()
    plt.savefig(f'resources\\images\\SPP\\Диффузное солнечное излучение (отражённое от воды), падающее на наклонную поверхность.png')
    plt.clf()

def create_images_radiation_inclined_surface(G):
    G['poa_global'].plot(figsize=(6.4, 4.8), label='Суммарное СИ')
    G['poa_direct'].plot(label='Прямое СИ')
    G['poa_diffuse'].plot(label='Диффузное СИ')
    plt.legend()
    plt.grid(linestyle='--')
    plt.ylabel('Солнечное излучение, Вт/кв.м')
    plt.xlabel('Номер часа в году')
    # plt.title('Солнечное излучение, падающее на наклонную поверхность')
    # plt.show()
    plt.savefig(f'resources\\images\\SPP\\Солнечное излучение, падающее на наклонную поверхность_2.png')
    plt.clf()

def create_images_optimization_tilt_angle(TiltedSurface):
    x = TiltedSurface['surf_tilt']
    y = TiltedSurface['Gsum_year']
    plt.figure(figsize=(6.4, 4.8))
    plt.plot(x, y)
    plt.grid(linestyle='--')
    plt.ylabel('Годовая сумма солнечного излучения, МВтч/кв.м')
    plt.xlabel('Угол установки приёмной поверхности, град.')
    # plt.title('Оптимизация угла наклона поверхности к горизонту')
    # plt.show()
    plt.savefig(f'resources\\images\\SPP\\Угол установки приёмной поверхности.png')
    plt.clf()

def create_images_radiation_during_year(i):
    plt.figure(figsize=(6.4, 4.8))
    plt.bar(range(1, 13), i['Global'])
    plt.grid(linestyle='--')
    plt.ylabel('Месячные суммы суммарного солнечного излучения, кВтч/кв.м')
    plt.xlabel('Номер месяца в году')
    # plt.title('Изменение солнечного излучения в течение года')
    # plt.show()
    plt.savefig(f'resources\\images\\SPP\\Месячные суммы суммарного солнечного излучения.png')
    plt.clf()

def create_images_temperature_calculation(temp, data, name):
    temp.plot(figsize=(6.4, 4.8), label='PVGIS')
    data['temp_air'].plot(label='Ta - pvgis')
    plt.legend()
    plt.grid(linestyle='--')
    plt.ylabel('Температура, град.C')
    plt.xlabel('Номер часа в году')
    # plt.title(f'Температура окр.воздуха и солнечных элементов ({name})')
    # plt.show()
    plt.savefig(f'resources\\images\\SPP\\Температура ФЭМ ({name}).png')
    plt.clf()

def create_images_building_vah(STC, name):
    i = STC['i']
    v = STC['v']

    fig, ax = plt.subplots(figsize=(6.4, 4.8))
    # ax.set_title(f'Вольт-амперная характеристика ФЭМ при стандартных условиях ({name})')
    # plt.figure(figsize=(16, 8))
    ax.plot(v, i, color='red', label='ВАХ')
    ax.set_xlabel('Напряжение')
    ax.set_ylabel('Ток, А')
    ax.legend(loc=2)
    ax2 = ax.twinx()
    ax2.plot(v, i * v, color='blue', label='Мощностная характеристика')
    ax2.set_ylabel('Мощность, Вт')
    ax2.legend(loc=3)
    ax.grid(linestyle='--')
    # plt.show()
    plt.savefig(f'resources\\images\\SPP\\ВАХ ({name}).png')
    plt.close(fig)

def create_images_power_single_diode(diode, name):
    diode['p_mp'].plot(figsize=(6.4, 4.8), label='p_mp')
    plt.legend()
    plt.grid(linestyle='--')
    plt.ylabel('Мощность ФЭМ, Вт.')
    plt.xlabel('Номер часа в году')
    # plt.title(f'Мощность единичного ФЭМ (в точке максимальной мощности) ({name})')
    # plt.show()
    plt.savefig(f'resources\\images\\SPP\\Мощность единичного ФЭМ ({name}).png')
    plt.clf()

def created_images_h_pod(data, name):
    # Получаем значения value и z
    x_values = [month_data['value'] for month, month_data in data.items()]
    y_values = [month_data['z'] for month, month_data in data.items()]

    # Получаем список месяцев
    months = list(data.keys())

    # Сортируем точки по значению value
    sorted_points = sorted(zip(x_values, y_values, months))

    # Разделяем отсортированные значения
    sorted_x, sorted_y, sorted_months = zip(*sorted_points)

    # Строим график, начиная с точки с наименьшим значением
    plt.plot(sorted_x, sorted_y, marker='o', linestyle='-')

    # Отображаем метки месяцев и их соответствующие цвета
    for x, y, month in zip(sorted_x, sorted_y, sorted_months):
        plt.text(x, y, month, fontsize=10, ha='right', va='bottom', bbox=dict(facecolor='white', alpha=0.5))


    # Добавляем заголовок и подписи осей
    # plt.title('График')
    plt.xlabel('Q, м$^3$')
    plt.ylabel('Z, м')

    # Показываем сетку на графике
    plt.grid(True)

    # Показываем график
    # plt.show()
    plt.savefig(f'resources\\images\\HPS\\Зависимость отметок уровня воды от расхода {name}.png')
    plt.clf()