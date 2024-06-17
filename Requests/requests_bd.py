def get_models_hps(connect, Hmin, Hmax, Q):
    cursor = connect.cursor()
    cursor.execute("SELECT * "
                   "FROM ГА "
                   "WHERE H_max >= %s "
                   "AND Q_min <= %s",
                   (Hmax, Q))
    results = cursor.fetchall()
    cursor.close()
    return results

def get_models_hps_new(connect, Hmin, Hmax, Q):
    cursor = connect.cursor()
    cursor.execute("SELECT * "
                   "FROM ГА "
                   "WHERE H_min <= %s AND H_max >= %s "
                   "AND Q_min <= %s",
                   (Hmin, Hmax, Q))
    results = cursor.fetchall()
    cursor.close()
    return results


def get_q(connect):
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM Среднемесячные_расходы")
    Q = cursor.fetchall()
    cursor.close()
    return Q


def get_load(connect):
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM Нагрузка_copy")
    load = cursor.fetchall()
    load = [i['Нагрузка'] for i in load]
    cursor.close()
    return load


def get_auxiliary_equipment(connect, group_ges):
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM Группа_ГЭС WHERE id = %s", group_ges)
    equipment = cursor.fetchall()
    cursor.close()
    return equipment


def get_model_ges(connect, h):
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM Тип_здания_ГЭС WHERE H_min <= %s AND H_max >= %s", (h, h))
    model_ges = cursor.fetchall()
    cursor.close()
    return model_ges


def add_turbines(connect):
    turbine = {
        "Company": "ИНСЭТ",
        "GA": "ГА-11",
        "Model_turbine": "РО160-78",
        "Name_type": "Радиально-осевая турбина",
        "Power_min": "1250",
        "Power_max": "5600",
        "H_min": "100",
        "H_max": "160",
        "Q_min": "1.5",
        "Q_max": "4.0",
        "U": "6000",
        "F": "50",
        "V_min": "600",
        "V_max": "1000",
        "M": "0",
        "Height": "0",
        "Weight": "0",
        "Leng": "0",
        "d": "800",
        "Price": "0"
    }
    cursor = connect.cursor()

    columns = ', '.join(turbine.keys())
    values_template = ', '.join(['%s'] * len(turbine))
    query = f"INSERT INTO ГА ({columns}) VALUES ({values_template})"

    cursor.execute(query, tuple(turbine.values()))
    connect.commit()


def add_cur(connect, a, b, c, table, column):

    print(column)
    cursor = connect.cursor()
    cursor.execute(f"DELETE FROM {table}")
    connect.commit()
    min_length = min(len(a), len(b), len(c))
    for i in range(min_length):
        cursor.execute(f"INSERT INTO {table} (id, {column}) VALUES (%s, %s, %s, %s)", (i+1, a[i], b[i], c[i]))
        connect.commit()


def get_cur(connect, table, column):
    if len(column.split(', ')) == 4:
        s1, s2, s3, s4 = column.split(', ')
        cursor = connect.cursor()
        cursor.execute(f"SELECT {column} FROM {table}")
        param = cursor.fetchall()
        a = [d[s1] for d in param]
        b = [d[s2] for d in param]
        c = [d[s3] for d in param]
        d = [d[s4] for d in param]
        cursor.close()
        return a, b, c, d
    else:
        s1, s2, s3 = column.split(', ')
        cursor = connect.cursor()
        cursor.execute(f"SELECT {column} FROM {table}")
        param = cursor.fetchall()
        a = [d[s1] for d in param]
        b = [d[s2] for d in param]
        c = [d[s3] for d in param]

        cursor.close()
        return a, b, c


def get_param_operator(connect, columns):
    cursor = connect.cursor()
    cursor.execute(f"SELECT {columns} FROM Параметры_оператора_ГЭС")
    param = list(cursor.fetchall()[0].values())

    cursor.close()
    return param


def get_param_operator_ses(connect, columns):
    cursor = connect.cursor()
    cursor.execute(f"SELECT {columns} FROM Параметры_оператора_СЭС")
    param = list(cursor.fetchall()[0].values())

    cursor.close()
    return param
