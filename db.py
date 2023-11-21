import os
import sqlite3
import time


def cancel_settings(con, cur, db_path):
    print("Отмена настроек. Выход из программы.")
    cur.close()
    con.close()
    os.remove(db_path)
    time.sleep(1)
    exit()


def finish_settings(con, cur):
    con.commit()
    cur.close()
    con.close()
    print("Сохранение | загрузка настроек.")
    time.sleep(1)


def input_language():
    lang = input('Введите язык вывода (en / ru):\n')

    while lang and (lang != 'ru' and  lang != 'en'):
        lang = input('Введите "ru" (Русский) или "en" (Английский). Для отмены настроек нажмите Enter.\n')
    return lang


def input_token():
    token = input('Введите ваш API токен сервиса DaData:\n')
    while token and len(token) != 40:
        token = input('Длина токена не равна 40. Введите его повторно. Нажмите Enter для отмены.\n')
    return token


def create_settings_database(db_name):
    try:
        try:
            con = sqlite3.connect(db_name)
        except sqlite3.DatabaseError:
            print('Ошибка открытия настроек. Возможно, у вас недостаточно прав.')
            time.sleep(1)
            exit()

        cursor = con.cursor()

        cursor.execute("""CREATE TABLE settings
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,  
                        parameter TEXT NOT NULL, 
                        value TEXT NOT NULL)
                    """)

        lang = input_language()
        if not lang:
            cancel_settings(con, cursor, db_name)
        token = input_token()
        if not token:
            cancel_settings(con, cursor, db_name)
        url = 'https://dadata.ru/'
        cursor.executemany("INSERT INTO settings (parameter, value) VALUES (?, ?)",
                           [('language', lang), ('token', token), ('url', url)])

        finish_settings(con, cursor)
        Settings.set_parameter('iscorrect', True)
    #except Exception as e:  # в случае, если мы закрыли программу самостоятельно, не записав данные в БД (она создалась, а данных нет - некорректно
        #os.remove(db_name)
    finally:
        if not Settings.get_parameter('is_correct'):
            os.remove(db_name)


def view_settings_from_db(db_name):
    try:
        con = sqlite3.connect(db_name)
    except sqlite3.DatabaseError:
        print('Ошибка открытия настроек. Возможно, у вас недостаточно прав.')
        time.sleep(1)
        exit()

    cursor = con.cursor()
    print('параметр - значение')
    for parameter in (['language', 'token', 'url']):
        cursor.execute("SELECT value FROM settings WHERE parameter = ?", (parameter, ))
        print(parameter, '-', cursor.fetchall()[0][0])


class Settings(object):
    __language = ''
    __token = ''
    __url = ''
    __iscorrect = False

    @classmethod
    def db_open(cls, db_name):
        try:
            con = sqlite3.connect(db_name)
            return con
        except sqlite3.DatabaseError:
            print('Ошибка открытия настроек. Возможно, у вас недостаточно прав.')
            time.sleep(1)
            exit()

    @classmethod
    def set_parameters_to_db(cls, db_name):
        connection = cls.db_open(db_name)
        cursor = connection.cursor()
        for parameter in (['language', 'token', 'url']):
            value = cls.get_parameter(parameter)
            cursor.execute("UPDATE settings SET value = ? WHERE parameter = ?", (value, parameter))
        finish_settings(connection, cursor)


    @classmethod
    def set_parameters_from_db(cls, db_name):
        connection = cls.db_open(db_name)
        cursor = connection.cursor()
        for parameter in (['language', 'token', 'url']):
            cursor.execute("SELECT value FROM settings WHERE parameter = ?", (parameter, ))
            cls.set_parameter(parameter, cursor.fetchall()[0][0])
        finish_settings(connection, cursor)

    @classmethod
    def get_parameter(cls, par_name):
        return getattr(cls, '_Settings__' + par_name)

    @classmethod
    def set_parameter(cls, par_name, value):
        setattr(cls, '_Settings__' + par_name, value)

    @classmethod
    def view_settings(cls):
        for parameter in (['language', 'token', 'url']):
            print(parameter, '-', Settings.get_parameter(parameter))
