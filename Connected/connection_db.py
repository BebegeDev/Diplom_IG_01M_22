import configparser

import pymysql
from pymysql.cursors import DictCursor
"""
    Подключение к удаленной БД для доступа к моделям оборудования
"""


def add_user():
    # Получаем данные пользователя из функции
    # config = configparser.ConfigParser()
    # config.read("Utill/setting.ini")
    # host = config['BD']['HOST']
    # user = config['BD']['USER']
    # password = config['BD']['PASSWORD']
    # BD = config['BD']['BD_NAME']
    try:
        connect = pymysql.connect(
            host='10.2.173.169',
            port=3306,
            user='alex',
            password='ijs900u',
            cursorclass=DictCursor,
            database='diplom_test',
            autocommit=True
        )

        return connect
    except Exception as e:
        print("Подключение не удалось")
        print(e)
        raise
