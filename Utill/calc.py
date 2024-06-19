import numpy as np
import pandas as pd


def calc_data(data, interval):
    a = [i for i in data for _ in range(interval)]
    a = a + a[:interval]
    b = []
    for i in range(len(a) - interval):
        if i < len(a):
            b.append(round(sum(a[i:i + interval]) / interval, 3))

    return b


def adjustment_annual_runoff(f, df_low, df_medium, period):
    df_low.reset_index(drop=True, inplace=True)
    df_medium.reset_index(drop=True, inplace=True)
    months_to_adjust = df_low.columns[df_low.iloc[0] > df_medium.iloc[0]]
    months_to_adjust_str = ', '.join(months_to_adjust)

    f.write(f"<p>Месяца для корректировки ({period}): {months_to_adjust_str}</p>")

    df_adjusted_medium = df_medium.copy()

    adjustments = []

    for month in months_to_adjust:
        excess_value = df_low.at[0, month] - df_medium.at[0, month]

        for m in df_medium.columns:
            if m != month and df_adjusted_medium.at[0, m] - excess_value > df_low.at[0, m]:
                df_adjusted_medium.at[0, m] -= excess_value
                df_adjusted_medium.at[0, month] += excess_value
                adjustments.append((month, m, excess_value))
                break

    f.write("<pre>Новый средневодный год после корректировки:</pre>")
    f.write(df_adjusted_medium.to_html(index=False))

    f.write("<pre>Корректировки (месяц, откуда убавили, куда добавили, сколько убавили):</pre>")
    f.write("<ul>")
    for adjustment in adjustments:
        f.write(f"<li>{adjustment}</li>")
    f.write("</ul>")

    return df_adjusted_medium


def calc_hourly_power_consumption(i, name, data):
    df = pd.DataFrame.from_dict(data, orient='index')
    df = df.rename_axis('Month').reset_index()

    month_order = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
                   'Ноябрь', 'Декабрь']
    df['Month'] = pd.Categorical(df['Month'], categories=month_order, ordered=True)
    df = df.sort_values('Month')

    days_in_month = {
        'Январь': 31, 'Февраль': 28, 'Март': 31, 'Апрель': 30, 'Май': 31, 'Июнь': 30, 'Июль': 31, 'Август': 31,
        'Сентябрь': 30, 'Октябрь': 31, 'Ноябрь': 30, 'Декабрь': 31
    }
    df['Days'] = df['Month'].map(days_in_month)

    df['Energy_kWh_per_hour'] = df['power']
    hourly_energy = []
    for _, row in df.iterrows():
        month_hours = row['Days'] * 24
        hourly_energy.extend([row['Energy_kWh_per_hour']] * month_hours)
    df = pd.DataFrame(hourly_energy)
    df.to_csv(f'resources\\file\\HPS\\ГЭС {name} кол-во ГА {i}.csv',
              index=False, header=False)


def create_sum_year_h_power(df1, df2, df3):
    df1 = pd.DataFrame({'Power_SES': df1})
    df2 = list(map(float, df2))
    df3 = list(map(float, df3))
    df4 = (df1['Power_SES'] + df3).tolist()
    df5 = np.array(df4) - np.array(df2)
    df2 = pd.DataFrame({'Load': df2}, index=df1.index)
    df3 = pd.DataFrame({'Power_GES': df3}, index=df1.index)
    df4 = pd.DataFrame({'Power_GES + Power_SES': df4}, index=df1.index)
    df5 = pd.DataFrame({'Power_summ - Load': df5}, index=df1.index)
    return [df1, df2, df3, df4, df5], [
        (df1, 'Power_SES'),
        (df2, 'Load'),
        (df3, 'Power_GES'),
        (df4, 'Power_GES + Power_SES'),
        (df5, 'Power_summ - Load')
    ]


def create_sum_year_m_power(df, column_name):
    monthly_sum = df.resample('ME').sum()  # Ресемплинг по месяцам и расчет суммы значений
    monthly_sum[column_name] = monthly_sum[column_name] / 1000
    return monthly_sum


def create_sum_year_d_power(df, column_name):
    daily_sum = df.resample('D').sum()  # Ресемплинг по дням и расчет суммы значений
    daily_sum[column_name] = daily_sum[column_name]  # Делим на 1000
    return daily_sum


def calc_z_v_f(z, f):
    v_list = []
    for i, k in enumerate(z):
        v = 0.7 * f[i] * pow(10, 6) * (k - z[0]) / pow(10, 9)
        v_list.append(v)


def open_exel(name):
    # Чтение данных из файла Excel
    df = pd.read_excel(name)

    # Преобразование данных в нужный формат
    data = []
    for index, row in df.iterrows():
        record = {'id': index + 1, 'Год': row['Год']}
        for month in range(1, 13):
            month_name = df.columns[month]
            record[month_name] = float(str(row[month_name]).replace(',', '.'))
        data.append(record)

    return data


def calc_energy_hps(name, data):
    # Преобразование данных в DataFrame
    df = pd.DataFrame.from_dict(data, orient='index')
    df = df.rename_axis('Month').reset_index()
    # Добавление количества дней в каждом месяце (учитывая невисокосный год)
    days_in_month = {
        'Январь': 31, 'Февраль': 28, 'Март': 31, 'Апрель': 30, 'Май': 31, 'Июнь': 30, 'Июль': 31, 'Август': 31,
        'Сентябрь': 30, 'Октябрь': 31, 'Ноябрь': 30, 'Декабрь': 31
    }

    # Добавление количества дней в DataFrame
    df['Days'] = df['Month'].map(days_in_month)

    # Расчет выработки электроэнергии в kWh
    df['Energy_kWh_per_hour'] = df['power']  # kW to kWh (за час)
    print(df['power'])
    df['Energy_kWh_per_day'] = df['Energy_kWh_per_hour'] * 24
    df['Energy_kWh_per_month'] = df['Energy_kWh_per_day'] * df['Days']


    # Сохранение в файл Excel
    df.to_excel(f'resources\\file\\HPS\\{name}_energy_output.xlsx', index=False)

    return df
