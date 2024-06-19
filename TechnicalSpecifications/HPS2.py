import math
import pandas as pd
import numpy as np


class SmallHPS:

    def __init__(self):
        self.f_list = None
        self.z_list = None
        self.name_list_ga = None
        self.data_list = None
        self.v_list = None
        self.z_wint = None
        self.z_summ = None
        self.q_wint = None
        self.q_summ = None
        self.min_value_rounded = None
        self.max_value_rounded = None
        self.yearly_averages = []
        self.power_min = None

        self.q_calc_min = None
        self.total_average_q = None
        self.q_calc = None
        self.h = None

    def calc_h(self, npu, unb):
        """
        Расчет напора
        :param npu: нормальный подпорный уровень
        :param unb: уровень нижнего бьефа
        :return: напор
        """
        self.h = npu - unb

    def calculate_total_average(self, q):
        """
        Расчет среднего многолетнего расхода
        :param q:
        :return: средний многолетний расход
        """

        total_sum = 0
        total_count = 0
        for year_data in q:
            for month, value in year_data.items():
                if month != 'id' and month != 'Год':
                    total_sum += value
                    total_count += 1

        self.total_average_q = total_sum / total_count
        return self.total_average_q




    def calc_security_curves(self, q):
        average_value = []
        for n, y in enumerate(q):
            year = y["Год"]
            average_value.append([value for key, value in y.items() if key not in ['id', 'Год']])
            self.yearly_averages.append([sum(average_value[n]) / 12, year])
        self.yearly_averages = pd.DataFrame(self.yearly_averages, columns=['Qrt', 'Годы_ср_г'])

        above_average = []
        below_average = []
        for index, row in self.yearly_averages.iterrows():
            qrt = row['Qrt']
            year = row['Годы_ср_г']
            year_list_above = []
            year_list_below = []
            for i in average_value[index]:
                if qrt > i:
                    year_list_above.append(i)
                else:
                    year_list_below.append(i)
            above_average.append([sum(year_list_above) / len(year_list_above), year])
            below_average.append([sum(year_list_below) / len(year_list_below), year])
        df_p = pd.DataFrame(below_average, columns=["Qпi", 'Годы_п'])
        df_m = pd.DataFrame(above_average, columns=["Qмi", 'Годы_м'])
        self.yearly_averages = self.yearly_averages.sort_values(by='Qrt', ascending=False)
        self.yearly_averages = self.yearly_averages.reset_index(drop=True)
        df_p = df_p.sort_values(by='Qпi', ascending=False)
        df_p = df_p.reset_index(drop=True)
        df_m = df_m.sort_values(by='Qмi', ascending=False)
        df_m = df_m.reset_index(drop=True)
        p = []
        for n in range(len(q)):
            p.append(((1 + n) / (len(self.yearly_averages) + 1)) * 100)
        self.yearly_averages["P,%"] = p

        self.yearly_averages = pd.concat([self.yearly_averages, df_p], axis=1)
        self.yearly_averages = pd.concat([self.yearly_averages, df_m], axis=1)
        return self.yearly_averages

    def q_min_q_max(self):
        min_value = self.yearly_averages[['Qrt', 'Qпi', 'Qмi']].min().min()
        max_value = self.yearly_averages[['Qrt', 'Qпi', 'Qмi']].max().max()
        self.min_value_rounded = math.floor(min_value)
        self.max_value_rounded = math.ceil(max_value)

    def calc_summ_wint_q(self):
        self.q_summ = np.linspace(self.min_value_rounded, self.max_value_rounded, num=10)
        self.q_wint = self.q_summ * 0.65

    def calc_summ_wint_z(self, z):
        self.z_summ = [pow(q, 1/3) + z for q in self.q_summ]
        self.z_wint = [pow(q, 1/3) + z for q in self.q_wint]

    def calc_z_v_f(self, df):
        self.z_list = df['z'].tolist()
        self.f_list = df['f'].tolist()
        self.v_list = []
        for i, k in enumerate(self.z_list):
            v = 0.7 * self.f_list[i] * pow(10, 6) * (k-self.z_list[0])/pow(10, 9)
            self.v_list.append(v)

    def checking_work_GA(self, GA_list, data, k, q_min, f):
        self.data_list = []
        self.name_list_ga = []
        self.list_power = []
        f.write("<h2>Выбор ГА</h2>")
        for ga in GA_list:
            ga_df = pd.DataFrame([ga])
            ga_print = ga_df
            for n in range(1, 4):
                power = n * ga['Power_max']
                new_data = {}
                for m, value in data.items():
                    if value['h'] < ga_df['H_min'].iloc[0]:
                        new_data[m] = {'power': 0}
                    else:
                        if ga_df['Q_max'].iloc[0] * n >= value['q'] >= ga_df['Q_min'].iloc[0] * n:

                            new_data[m] = {'power': k * value['q'] * value['h']}
                        elif value['q'] < ga_df['Q_min'].iloc[0] * n and value['q'] >= ga_df['Q_min'].iloc[0]:
                            n_new = math.floor(value['q'] / ga_df['Q_min'].iloc[0])
                            new_data[m] = {'power':k * value['q'] * value['h']}
                        elif value['q'] > ga_df['Q_max'].iloc[0] * n:
                            new_data[m] = {'power': k * ga_df['Q_max'].iloc[0] * value['h']}

                total_power = sum(values['power'] for values in new_data.values())
                if total_power != 0:
                    self.list_power.append(power)
                    f.write(f"<h3>{ga['GA']}</h3>")
                    f.write("<table border='1'>")
                    f.write("<tr><th>Parameter</th><th>Value</th></tr>")
                    for col in ga_print.columns:
                        f.write(f"<tr><td>{col}</td><td>{ga_print[col].iloc[0]}</td></tr>")
                    f.write("</table>")
                    self.name_list_ga.append(ga['GA'])
                    f.write(f"<p>Количество ГА: {n}</p>")
                    f.write(f"<p>Установленная мощность: {power}</p>")
                    f.write("<h4>ПРЕДУПРЕЖДЕНИЕ</h4>")
                    for m, value in data.items():
                        if value['h'] < ga_df['H_min'].iloc[0]:
                            f.write(f"<p>{ga_df['GA'].iloc[0]} В {m.upper()}: НАПОР {value['h']} "
                                    f"МЕНЬШЕ ДОПУСТИМО ВОЗМОЖНОГО {ga_df['H_min'].iloc[0]} Т.О, "
                                    f"СТАНЦИЯ НЕ СМОЖЕТ ВЫРАБАТЫВАТЬ ЭЛЕКТРОЭНЕРГИЮ В ЭТОМ МЕСЯЦЕ.</p>")
                        else:
                            if ga_df['Q_max'].iloc[0] * n < value['q']:
                                f.write(f"<p>{ga_df['GA'].iloc[0]} В {m.upper()}: ПРИТОК {value['q']} "
                                        f"БОЛЬШЕ ПРОПУСКНУОЙ СПОСОБНОСТИ ГА {ga_df['Q_max'].iloc[0] * n} Т.О, СТАНЦИЯ СМОЖЕТ ВЫРАБАТЫВАТЬ ЭЛЕКТРОЭНЕРГИЮ "
                                        "ТОЛЬКО ПО СВОЕЙ МАКСИМАЛЬНОЙ ПРОПУСКНОЙ СПОСОБНОСТИ</p>")
                                f.write(f"<p>МАКСИМАЛЬНАЯ МОЩНОСТЬ: {k * ga_df['Q_max'].iloc[0] * n * value['h']} "
                                        f"ИЗ ВОЗМОЖНОЙ {value['power']}</p>")
                                new_data[m] = {'power': k * ga_df['Q_max'].iloc[0] * value['h'] * n}
                    self.data_list.append([n, new_data])
                    f.write('<hr>')

        return self.data_list


    def print_new_power(self, f):
        days_in_month = {
            'Январь': 31, 'Февраль': 28, 'Март': 31, 'Апрель': 30, 'Май': 31, 'Июнь': 30, 'Июль': 31, 'Август': 31,
            'Сентябрь': 30, 'Октябрь': 31, 'Ноябрь': 30, 'Декабрь': 31
        }
        n = [1,2,3] * len(self.data_list)
        for name, ga in enumerate(self.data_list):
            ee_year = 0
            power = self.list_power[name]
            _, ga = ga
            f.write(f"<h3>ГА: {self.name_list_ga[name]} кол-во ГА {n[name]}</h3>")
            f.write("<table border='1'>")
            f.write("<tr><th>Месяц</th>"
                    "<th>Мощность</th>"
                    "<th>Выработка в чач</th>"
                    "<th>Выработка в день</th>"
                    "<th>Выработка в месяц</th>"
                    "</tr>")
            for m, value in ga.items():
                d = days_in_month[m]
                ee_year += value['power'] * 24 * d
                f.write(f"<tr><td>{m}</td>"
                        f"<td>{value['power']}</td>"
                        f"<td>{value['power']}</td>"
                        f"<td>{value['power'] * 24}</td>"
                        f"<td>{value['power'] * 24 * d}</td>"
                        f"</tr>")
            f.write("</table>")
            f.write("<br>")
            f.write(
                f"<p>КИУМ {ee_year/(power * 8760)}</p>")

class SecurityCurves:

    def __init__(self, percent):
        self.year = None
        self.new_power = None
        self.average_power = None
        self.percent = percent
        self.npu = None
        self.autumn_winter_period = None
        self.spring_summer_period = None
        self.row = None
        self.result = None
        self.kp_two = None
        self.kp_one = None
        self.km_two = None
        self.km_one = None
        self.year_two = None
        self.year_one = None
        self.right = None
        self.left = None
        self.power = None
        self.combined_data = None
        self.h_pod_w = None
        self.h_pod_s = None
        self.m = {
            1: 'Январь',
            2: 'Февраль',
            3: 'Март',
            4: 'Апрель',
            5: 'Май',
            6: 'Июнь',
            7: 'Июль',
            8: 'Август',
            9: 'Сентябрь',
            10: 'Октябрь',
            11: 'Ноябрь',
            12: 'Декабрь'
        }

    def calc_conversion_factors(self, yearly_averages):
        self.left = yearly_averages[yearly_averages['P,%'] <= self.percent].iloc[-1]
        self.right = yearly_averages[yearly_averages['P,%'] >= self.percent].iloc[0]

        self.year_one = self.left['Годы_ср_г']
        self.year_two = self.right['Годы_ср_г']
        qmi_one = yearly_averages.loc[yearly_averages['Годы_м'] == self.year_one, 'Qмi'].values[0]
        qmi_two = yearly_averages.loc[yearly_averages['Годы_м'] == self.year_two, 'Qмi'].values[0]
        qpi_one = yearly_averages.loc[yearly_averages['Годы_п'] == self.year_one, 'Qпi'].values[0]
        qpi_two = yearly_averages.loc[yearly_averages['Годы_п'] == self.year_two, 'Qпi'].values[0]
        self.km_one = self.left["Qмi"] / qmi_one
        self.km_two = self.right["Qмi"] / qmi_two
        self.kp_one = self.left["Qпi"] / qpi_one
        self.kp_two = self.right["Qпi"] / qpi_two

    def calc_avg_monthly_year(self):
        k_one = abs(self.km_one - 1) + abs(self.kp_one - 1)
        k_two = abs(self.km_two - 1) + abs(self.kp_two - 1)
        if k_one < k_two:
            self.result = [self.km_one, self.kp_one, self.year_one]
        else:
            self.result = [self.km_two, self.kp_two, self.year_two]


    def get_avg_monthly_year(self):
        return self.result

    def calc_annual_runoff(self, summ, wint, q):
        q = pd.DataFrame(q)

        km, kp, self.year = self.get_avg_monthly_year()
        self.row = q[q['Год'] == self.year]
        spring_summer_period = summ
        spring_summer_period = [int(x) for x in spring_summer_period.split(",")]
        autumn_winter_period = wint
        autumn_winter_period = [int(x) for x in autumn_winter_period.split(",")]
        spring_summer_period = [self.m[num] for num in spring_summer_period]
        autumn_winter_period = [self.m[num] for num in autumn_winter_period]

        self.spring_summer_period = self.row[spring_summer_period] * km
        self.autumn_winter_period = self.row[autumn_winter_period] * kp

    def calc_h_pod(self, pol, mej, q_s, q_w, z_s, z_w):
        self.h_pod_s = self.interpolate_z(pol, q=q_s, z=z_s)
        self.h_pod_w = self.interpolate_z(mej, q=q_w, z=z_w)

    @staticmethod
    def interpolate_z(df, q, z):
        results = {}
        for col in df.columns:
            value = df[col][0]
            interpolated_z = np.interp(value, q, z)
            results[col] = {'value': value, 'z': interpolated_z}
        return results

    def get_h_pod_s(self):
        return self.h_pod_s

    def get_h_pod_w(self):
        return self.h_pod_w

    def calc_supplied_pressure(self, npu):
        self.result = {}
        self.npu = npu
        self.combined_data = {**self.get_h_pod_w(), **self.get_h_pod_s()}
        for m, value in self.combined_data.items():
            self.result[m] = {'h': npu - value['z'] - 1, 'z': value['z'], 'q': value['value']}

    def calc_power(self, k, f):
        self.power = {}
        f.write("<h2>Мощность по месяцам</h2>")
        f.write("<table border='1'><tr><th>Месяц</th><th>Напор</th><th>З</th><th>Приток</th><th>Мощность</th></tr>")
        for m, value in self.result.items():
            self.power[m] = {'power': k * value['q'] * value['h'], 'h': value['h'], 'q': value['q']}
            f.write(
                f"<tr><td>{m}</td><td>{value['h']}</td><td>{value['z']}</td><td>{value['q']}</td><td>{k * value['q'] * value['h']}</td></tr>")
        f.write("</table>")
        return self.power

    def calc_total_power(self):
        total_power = sum(month_data['power'] for month_data in self.power.values())
        self.average_power = total_power / len(self.power)
        return self.average_power

    def get_power_h_q_max_min(self):
        min_power_month = min(self.power, key=lambda x: self.power[x]['power'])
        max_power_month = max(self.power, key=lambda x: self.power[x]['power'])
        min_power = self.power[min_power_month]['power']
        max_power = self.power[max_power_month]['power']

        # Найдем минимальный и максимальный напор
        min_h_month = min(self.power, key=lambda x: self.power[x]['h'])
        max_h_month = max(self.power, key=lambda x: self.power[x]['h'])
        min_h = self.power[min_h_month]['h']
        max_h = self.power[max_h_month]['h']

        # Найдем минимальный и максимальный напор
        min_q_month = min(self.power, key=lambda x: self.power[x]['q'])
        max_q_month = max(self.power, key=lambda x: self.power[x]['q'])
        min_q = self.power[min_q_month]['q']
        max_q = self.power[max_q_month]['q']

        return min_power, max_power, min_h, max_h, min_q, max_q
