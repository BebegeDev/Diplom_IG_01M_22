import datetime
import pandas as pd
import pvlib
import math
import numpy as np


class Sun:

    def __init__(self, latitude, longitude, altitude, loc, year, surface_tilt, surface_azimuth, albedo):

        self.G = None
        self.__location_determination(latitude, longitude, altitude, loc)
        self.__defining_modeling_period(year)
        self.__determining_position_sun_in_sky()
        self.__determination_solar_radiation_up_boundary_atmosphere()
        self.__getting_data_pvgis_db(year)
        self.__let_determine_offset_relative_utc()
        self.__calculation_isotropic_celestial_sphere(surface_tilt)
        self.__calculation_anisotropic_celestial_sphere(surface_tilt, surface_azimuth)
        self.__calculation_solar_radiation_reflected_water(albedo, surface_tilt)
        self.__determining_angle_incidence(surface_tilt, surface_azimuth)
        self.__determine_components_solar_radiation()
        self.__calc_direct_normal_irradiance()
        self.__calc_monthly_solar_radiation(year)

    def __location_determination(self, latitude, longitude, altitude, loc):
        self.__loc = pvlib.location.Location(
            latitude,
            longitude,
            altitude=altitude,
            tz=loc)


    def get_location_determination(self):
        return self.__loc

    def __determining_position_sun_in_sky(self):
        self.__SPA = pvlib.solarposition.spa_python(self.get_defining_modeling_period(),
                                                    self.get_location_determination().latitude,
                                                    self.get_location_determination().longitude,
                                                    altitude=self.get_location_determination().altitude)

    def get_determining_position_sun_in_sky(self):
        return self.__SPA

    def __defining_modeling_period(self, year):
        self.__times = pd.date_range(start=datetime.datetime(year, 1, 1),
                                     end=datetime.datetime(year, 12, 31, 23),
                                     freq='1h').tz_localize(tz=self.get_location_determination().tz)

    def get_defining_modeling_period(self):
        return self.__times

    def __determination_solar_radiation_up_boundary_atmosphere(self):
        self.__DNI_extra = pvlib.irradiance.get_extra_radiation(self.__times,
                                                                solar_constant=1366.1,
                                                                method='spencer')

    def get_determination_solar_radiation_up_boundary_atmosphere(self):
        return self.__DNI_extra

    def __getting_data_pvgis_db(self, year):
        self.__PVGIS_data, self.__PVGIS_inputs, self.__PVGIS_metadata = pvlib.iotools.get_pvgis_hourly(
            self.__loc.latitude,
            self.__loc.longitude,
            start=year,
            end=year,
            raddatabase=None,
            components=True,
            surface_tilt=0,
            surface_azimuth=180,
            outputformat='json',
            usehorizon=True,
            userhorizon=None,
            pvcalculation=False,
            peakpower=None,
            pvtechchoice='crystSi',
            mountingplace='free',
            loss=0,
            trackingtype=0,
            optimal_surface_tilt=False,
            optimalangles=False,
            url='https://re.jrc.ec.europa.eu/api/',
            map_variables=True,
            timeout=30)

    def get_pvgis_data(self):
        return self.__PVGIS_data

    def get_pvgis_inputs(self):
        return self.__PVGIS_inputs

    def get_pvgis_metadata(self):
        return self.__PVGIS_metadata

    def __let_determine_offset_relative_utc(self):
        data3 = None
        times_loc1 = self.__times[1]
        timezone = times_loc1.strftime('%z')
        timezone = timezone[0:3]
        timezone = int(timezone)
        # deltaTimeZone = +3
        data = self.get_pvgis_data()
        len_data = len(data)

        if timezone >= 0:
            data1 = data[len_data - timezone:len_data]
            data2 = data[0:len_data - timezone]
            # data3 = data1.append(data2, ignore_index = True)
            data3 = pd.concat([data1, data2], ignore_index=True)

        if timezone < 0:
            data1 = data[0:abs(timezone)]
            data2 = data[abs(timezone):len_data]
            # data3 = data2.append(data1, ignore_index = True)
            data3 = pd.concat([data2, data1], ignore_index=True)

        data3['time'] = self.__times
        data3 = data3.set_index('time')
        self.__PVGIS_data = data3

    def get_let_determine_offset_relative_utc(self):
        return self.__PVGIS_data

    def __calculation_isotropic_celestial_sphere(self,surface_tilt):
        self.__diffuse_sky_isotropic = pvlib.irradiance.isotropic(surface_tilt, self.__PVGIS_data['poa_sky_diffuse'])

    def get_calculation_isotropic_celestial_sphere(self):
        return self.__diffuse_sky_isotropic

    def __calculation_anisotropic_celestial_sphere(self, surface_tilt, surface_azimuth):
        self.__airmass_relative = pvlib.atmosphere.get_relative_airmass(
            self.get_determining_position_sun_in_sky()['zenith'],
            model='simple')

        self.__diffuse_sky_perez = pvlib.irradiance.perez(surface_tilt,
                                                          surface_azimuth,
                                                          self.__PVGIS_data['poa_sky_diffuse'],
                                                          self.__PVGIS_data['poa_direct'],
                                                          self.get_determination_solar_radiation_up_boundary_atmosphere(),
                                                          self.get_determining_position_sun_in_sky()['apparent_zenith'],
                                                          self.get_determining_position_sun_in_sky()['azimuth'],
                                                          self.__airmass_relative,
                                                          model='allsitescomposite1990',
                                                          return_components=False)

    def get_calculation_anisotropic_celestial_sphere(self):
        return self.__diffuse_sky_perez

    def __calculation_solar_radiation_reflected_water(self, albedo, surface_tilt):
        numbers_as_strings = albedo.split(',')
        albedo = [float(num) for num in numbers_as_strings]
        self.__albedo = self.__calc_albedo(albedo)

        data = self.__PVGIS_data['poa_direct'] + self.__PVGIS_data['poa_sky_diffuse']
        self.__diffuse_water = pvlib.irradiance.get_ground_diffuse(surface_tilt,
                                                                   data,
                                                                   albedo=self.__albedo['Albedo'].values,
                                                                   surface_type=None)

    def __calc_albedo(self, albedo):
        monthly_albedo = [float(value) for value in albedo]
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        hourly_albedo = []
        for month_index, albedo in enumerate(monthly_albedo):
            hours_in_month = days_in_month[month_index] * 24
            hourly_albedo.extend([albedo] * hours_in_month)
        assert len(hourly_albedo) == 8760, "Длина списка не равна 8760 часам"
        df = pd.DataFrame(hourly_albedo, columns=['Albedo'])
        df['Datetime'] = pd.date_range(start='2023-01-01', periods=8760, freq='h')
        df.set_index('Datetime', inplace=True)
        return df

    def get_calculation_solar_radiation_reflected_water(self):
        return self.__diffuse_water

    def __determining_angle_incidence(self, surface_tilt, surface_azimuth):
        self.__AOI = pvlib.irradiance.aoi(surface_tilt,
                                          surface_azimuth,
                                          self.get_determining_position_sun_in_sky()['zenith'],
                                          self.get_determining_position_sun_in_sky()['azimuth'])

    def get_determining_angle_incidence(self):
        return self.__AOI

    def __determine_components_solar_radiation(self):
        self.__components_solar_radiation = (
            pvlib.irradiance.poa_components(self.get_determining_angle_incidence(),
                                            self.__PVGIS_data['poa_direct'],
                                            self.get_calculation_anisotropic_celestial_sphere(),
                                            self.get_calculation_solar_radiation_reflected_water()))

    def get_determine_components_solar_radiation(self):
        return self.__components_solar_radiation

    def __calc_direct_normal_irradiance(self):
        pvgis_sum = self.__PVGIS_data['poa_direct'] + self.__PVGIS_data['poa_sky_diffuse']
        self.__direct_normal_irradiance = pvlib.irradiance.dni(pvgis_sum,
                                                               self.__PVGIS_data['poa_sky_diffuse'],
                                                               self.get_determining_position_sun_in_sky()['zenith'],
                                                               clearsky_dni=None,
                                                               clearsky_tolerance=1.1,
                                                               zenith_threshold_for_zero_dni=88.0,
                                                               zenith_threshold_for_clearsky_limit=80.0)

    def get_calc_direct_normal_irradiance(self):
        return self.__direct_normal_irradiance

    def determining_optimal_orientation(self, f):
        TiltedSurface = pd.DataFrame(columns=['surf_tilt', 'Gsum_year'])
        i = 0
        SA = [180]
        ST = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 40]
        pvgis_sum = self.__PVGIS_data['poa_direct'] + self.__PVGIS_data['poa_sky_diffuse']
        f.write(f"<pre>Суммарное солнечное излучение в плоскости заданной ориентации, МВтч/кв.м в год</pre>")
        f.write(f"<pre>(на основе данных полученных по моделям ясного неба):</pre>")
        f.write(f"<pre>GHI: {round(pvgis_sum.sum() / 1000000, 3)} </pre>")
        for surface_azimuth in SA:
            f.write(f"<pre>Азимут приёмной поверхности, град.: {surface_azimuth} </pre>")
            for surface_tilt in ST:
                diffuse_sky_perez = pvlib.irradiance.perez(surface_tilt,
                                                           surface_azimuth,
                                                           self.__PVGIS_data['poa_sky_diffuse'],
                                                           self.get_calc_direct_normal_irradiance(),
                                                           self.get_determination_solar_radiation_up_boundary_atmosphere(),
                                                           self.get_determining_position_sun_in_sky()
                                                           ['apparent_zenith'],
                                                           self.get_determining_position_sun_in_sky()['azimuth'],
                                                           self.__airmass_relative,
                                                           model='allsitescomposite1990',
                                                           return_components=False)

                diffuse_ground = pvlib.irradiance.get_ground_diffuse(surface_tilt,
                                                                     self.__PVGIS_data['poa_direct']
                                                                     + self.__PVGIS_data['poa_sky_diffuse'],
                                                                     albedo=self.__albedo['Albedo'].values,
                                                                     surface_type=None)

                AOI = pvlib.irradiance.aoi(surface_tilt,
                                           surface_azimuth,
                                           self.get_determining_position_sun_in_sky()['zenith'],
                                           self.get_determining_position_sun_in_sky()['azimuth'])

                self.G = pvlib.irradiance.poa_components(AOI,
                                                         self.get_calc_direct_normal_irradiance(),
                                                         diffuse_sky_perez,
                                                         diffuse_ground)

                g_sum = self.G['poa_global'].sum()
                TiltedSurface.loc[i, 'surf_tilt'] = surface_tilt  # в i-ую строчку dataframe запишем
                TiltedSurface.loc[i, 'Gsum_year'] = g_sum / 1000000  # соответствующие значения
                i = i + 1

                f.write(f"<pre>   Угол наклона поверхности: {surface_tilt}  град.: {round(g_sum / 1000000, 3)} "
                        f"прирост - : {round(g_sum / pvgis_sum.sum() * 100 - 100, 1)} %</pre>")

        tilted_surface = TiltedSurface.sort_values(by=['surf_tilt'])

        return tilted_surface

    def __calc_monthly_solar_radiation(self, year):
        self.__irradiance_surface = pd.DataFrame(index=range(12),
                                                 columns=['Month', 'Global', 'Diffuse', 'Direct'])
        date_range = None
        G = self.get_determine_components_solar_radiation()
        for mm in range(12):
            m = mm + 1
            if m == 1:
                date_range = G.loc[f'{year}-01-01':f'{year}-01-31']
            if m == 2:
                date_range = G.loc[f'{year}-02-01':f'{year}-02-28']
            if m == 3:
                date_range = G.loc[f'{year}-03-01':f'{year}-03-31']
            if m == 4:
                date_range = G.loc[f'{year}-04-01':f'{year}-04-30']
            if m == 5:
                date_range = G.loc[f'{year}-05-01':f'{year}-05-31']
            if m == 6:
                date_range = G.loc[f'{year}-06-01':f'{year}-06-30']
            if m == 7:
                date_range = G.loc[f'{year}-07-01':f'{year}-07-31']
            if m == 8:
                date_range = G.loc[f'{year}-08-01':f'{year}-08-31']
            if m == 9:
                date_range = G.loc[f'{year}-09-01':f'{year}-09-30']
            if m == 10:
                date_range = G.loc[f'{year}-10-01':f'{year}-10-31']
            if m == 11:
                date_range = G.loc[f'{year}-11-01':f'{year}-11-30']
            if m == 12:
                date_range = G.loc[f'{year}-12-01':f'{year}-12-31']

            self.__irradiance_surface.loc[mm, 'Month'] = m
            self.__irradiance_surface.loc[mm, 'Global'] = date_range['poa_global'].sum() / 1000
            self.__irradiance_surface.loc[mm, 'Diffuse'] = date_range['poa_diffuse'].sum() / 1000
            self.__irradiance_surface.loc[mm, 'Direct'] = date_range['poa_direct'].sum() / 1000


    def get_calc_monthly_solar_radiation(self):
        return self.__irradiance_surface


class SES:

    def __init__(self, sun, ses, name, a, b, delta_T):
        self.sun = sun
        self.ses = ses
        self.name = name
        self.__assessment_effective_irradiation()
        self.__temperature_calculation(a, b, delta_T)
        self.__building_vah()
        self.__calc_energy_prod_single_fem()
        self.__calc_s_ses()

    def __assessment_effective_irradiation(self):
        self.__effective_irradiance = self.sun.get_determine_components_solar_radiation()['poa_global'] * 0.97

    def get_assessment_effective_irradiation(self):
        return self.__effective_irradiance

    def __temperature_calculation(self, a, b, delta_T):
        self.__cells_temperature = (
            pvlib.temperature.sapm_cell(self.sun.get_determine_components_solar_radiation()['poa_global'],
                                        self.sun.get_let_determine_offset_relative_utc()[
                                            'temp_air'],
                                        self.sun.get_let_determine_offset_relative_utc()[
                                            'wind_speed'],
                                        a,
                                        b,
                                        delta_T,
                                        irrad_ref=1000.0))

    def get_temperature_calculation(self):
        return self.__cells_temperature

    def __building_vah(self):
        list_i = []
        list_v = np.linspace(0, self.ses['V_oc_ref'], 200)

        for v in list_v:
            list_i.append(pvlib.pvsystem.i_from_v(v,
                                                  self.ses['I_L_ref'],
                                                  self.ses['I_o_ref'],
                                                  self.ses['R_s'],
                                                  self.ses['R_sh_ref'],
                                                  self.ses['a_ref'],
                                                  method='lambertw'
                                                  ))
        self.__STC = {
            'v': list_v,
            'i': np.array(list_i),
        }

    def get_building_vah(self):
        return self.__STC

    def __calc_energy_prod_single_fem(self):
        photo_current, saturation_current, resistance_series, resistance_shunt, nNsVth = (
            pvlib.pvsystem.calcparams_desoto(
                pd.to_numeric(self.get_assessment_effective_irradiation()),
                pd.to_numeric(self.get_temperature_calculation()),
                self.ses['alpha_sc'],
                self.ses['a_ref'],
                self.ses['I_L_ref'],
                self.ses['I_o_ref'],
                self.ses['R_sh_ref'],
                self.ses['R_s'],
                EgRef=1.121,
                dEgdT=- 0.0002677,
                irrad_ref=1000,
                temp_ref=25))

        self.__diode = pvlib.pvsystem.singlediode(photo_current,
                                                  saturation_current,
                                                  resistance_series,
                                                  resistance_shunt,
                                                  nNsVth,
                                                  ivcurve_pnts=None,
                                                  method='newton')

    def get_calc_energy_prod_single_fem(self):
        return self.__diode

    def __calc_s_ses(self):
        self.__s = self.ses['Length'] * self.ses['Width']

    def get__calc_s_ses(self):
        return self.__s


class Inverter:

    def __init__(self, inv, name, ses, f):
        self.ses = ses
        self.inf = inv
        self.name = name
        self.__max_voltage_element()
        self.__calc_number_sequentially_m()
        self.__max_value_sh_circuit_i()
        self.__calc_number_parallel_m()
        self.__calculation_peak_battery_power()
        self.__load_factor_inverter()
        self.__calc_voltage_battery()
        self.__calc_power_battery()
        self.__power_generation_ac()
        self.__utilization_rate_installed_power_ac()
        self.__utilization_rate_installed_power_dc()
        self.__calc_space_ses()
        self.__calc_min_v(f)

    def __max_voltage_element(self):
        self.__voc_max = max(self.ses.get_calc_energy_prod_single_fem()['v_oc'].max(), self.ses.ses['V_oc_ref'])

    def get_max_voltage_element(self):
        return self.__voc_max

    def __calc_number_sequentially_m(self):
        self.__num_seq = int(math.modf(self.inf['Vdcmax'] / self.get_max_voltage_element())[1])

    def get_calc_number_sequentially_m(self):
        return self.__num_seq

    def __max_value_sh_circuit_i(self):
        self.__isc_max = max(self.ses.get_calc_energy_prod_single_fem()['i_sc'].max(), self.ses.ses['I_sc_ref'])

    def get_max_value_sh_circuit_i(self):
        return self.__isc_max

    def __calc_number_parallel_m(self):
        self.__num_par = int(math.modf(self.inf['Idcmax'] / self.get_max_value_sh_circuit_i())[1])

    def get_calc_number_parallel_m(self):
        return self.__num_par

    def __calculation_peak_battery_power(self):
        self.__pv_battery = (self.get_calc_number_sequentially_m() * self.get_calc_number_parallel_m() *
                             self.ses.ses['STC'])

    def get_calculation_peak_battery_power(self):
        return self.__pv_battery

    def __load_factor_inverter(self):
        self.__factor = round(self.get_calculation_peak_battery_power() / self.inf['Pdco'], 3)

    def get_load_factor_inverter(self):
        return self.__factor

    def __calc_voltage_battery(self):
        self.__voltage_battery = self.ses.get_calc_energy_prod_single_fem()[
                                     'v_mp'] * self.get_calc_number_sequentially_m()

    def get_calc_voltage_battery(self):
        return self.__voltage_battery

    def __calc_power_battery(self):
        self.__power_battery = (self.ses.get_calc_energy_prod_single_fem()['p_mp'] *
                                self.get_calc_number_sequentially_m() * self.get_calc_number_parallel_m())

    def get_calc_power_battery(self):
        return self.__power_battery

    def __power_generation_ac(self):
        self.__ac_out = pvlib.inverter.sandia(
            self.get_calc_voltage_battery(),
            self.get_calc_power_battery(),
            self.inf)

    def get_power_generation_ac(self):
        return self.__ac_out

    def __utilization_rate_installed_power_ac(self):
        self.__factor_ac = round(self.get_power_generation_ac().sum() / (self.inf['Paco'] * 8760) * 100, 2)

    def get_utilization_rate_installed_power_ac(self):
        return self.__factor_ac

    def __utilization_rate_installed_power_dc(self):
        self.__factor_dc = round(self.get_power_generation_ac().sum() / (self.ses.ses['STC'] *
                                                                         self.get_calc_number_sequentially_m() *
                                                                         self.get_calc_number_parallel_m()
                                                                         * 8760) * 100, 2)

    def get_utilization_rate_installed_power_dc(self):
        return self.__factor_dc

    def __calc_space_ses(self):
        self.__ses_space = (self.ses.get__calc_s_ses() *
                            self.get_calc_number_sequentially_m() * self.get_calc_number_parallel_m())

    def get_calc_space_ses(self):
        return self.__ses_space

    def __calc_min_v(self, f):
        self.__f = f * 1000000

    def get_calc_min_f(self):
        return self.__f
