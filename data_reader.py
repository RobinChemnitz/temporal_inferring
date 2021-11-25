import numpy as np
import xlrd
import settings


def read_city_database():
    sheet = xlrd.open_workbook('Data/city_database.xls').sheet_by_index(0)

    city_pos_geo = []
    city_states = []
    romanization_times = []
    city_info = []

    timeframes = sheet.ncols - 5

    for row in range(1, sheet.nrows):
        site_key = sheet.cell_value(row, 0)
        modern_name = sheet.cell_value(row, 1)
        latin_name = sheet.cell_value(row, 2)
        city_info.append([site_key, modern_name, latin_name])

        x = sheet.cell_value(row, 3)
        y = sheet.cell_value(row, 4)
        x = float(x)
        y = float(y)
        city_pos_geo.append([x, y])

        states = []
        t_rom = 0
        romanized = False
        for t in range(timeframes):
            state_t = ''
            state_string = sheet.cell_value(row, 5 + t)
            if 'civita' in state_string:
                state_t = 'civ'
            if 'municipium' in state_string:
                state_t = 'mun'
            if 'colonia' in state_string:
                state_t = 'col'
            if state_t and not romanized:
                romanized = True
                t_rom = t
            states.append(state_t)
        city_states.append(states)
        romanization_times.append(t_rom)

    city_info = np.array(city_info)
    city_states = np.array(city_states)
    city_pos_geo = np.array(city_pos_geo)
    romanization_times = np.array(romanization_times)

    np.save('Storage/city_info.npy', city_info)
    np.save('Storage/city_states.npy', city_states)
    np.save('Storage/city_pos_geo.npy', city_pos_geo)
    np.save('Storage/romanization_times.npy', romanization_times)

    settings.N_CITIES = len(city_info)
    settings.N_TIMEFRAMES = timeframes


def read_milestone_database():
    sheet = xlrd.open_workbook('Data/milestone_database.xls').sheet_by_index(0)

    ms_info = []
    ms_time = []
    ms_pos_geo = []

    for row in range(1, sheet.nrows):
        ms_key = sheet.cell_value(row, 0)
        site_key = sheet.cell_value(row, 1)
        ms_info.append([ms_key, site_key])

        start_date = sheet.cell_value(row, 2)
        end_date = sheet.cell_value(row, 3)
        start_date = float(start_date)
        end_date = float(end_date)
        time = (start_date + end_date) / 2
        ms_time.append(time)

        x = sheet.cell_value(row, 4)
        y = sheet.cell_value(row, 5)
        x = float(x)
        y = float(y)
        ms_pos_geo.append([x, y])

    ms_info = np.array(ms_info)
    ms_time = np.array(ms_time)
    ms_pos_geo = np.array(ms_pos_geo)

    np.save('Storage/milestone_info.npy', ms_info)
    np.save('Storage/milestone_times.npy', ms_time)
    np.save('Storage/milestone_pos_geo.npy', ms_pos_geo)
