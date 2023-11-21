import os.path
import time
import db
from dadata import Dadata
from httpx import HTTPStatusError
#import httpx

DB_PATH = 'sqlite_database_for_adress_to_coord_seeker.db'


def dadata_request(token, text, language):
    dadata = Dadata(token=token)
    return dadata.suggest("address", text, language=language)


def print_result(data):
    print('Найденные адреса:')
    for count, address in enumerate(data):
        print(f"{count + 1}. {address['value']}")


def request_text():
    return input("Для получения необходимых координат введите адрес в свободной форме. Чтобы вернуться, "
                 "нажмите Enter.\n")


def start_menu():
    return input("Меню:\n"
                 "1. Ввести запрос\n"
                 "2. Изменить настройки\n"
                 "3. Вывести настройки\n"
                 "Выберите номер пункта меню. Для выхода нажмите Enter\n")

def settings_menu():
    return input("Меню настроек:\n"
                 "1. Изменить язык вывода\n"
                 "2. Изменить API токен DaData\n"
                 "Выберите номер пункта меню. Чтобы вернуться, нажмите Enter\n")

def get_request_from_dadata(dadata_token, language):
    # заход в запрос по тексту
    while True:
        text = request_text()
        if not text:
            break
        try:
            result = dadata_request(dadata_token, text, language)
        except HTTPStatusError as e:
            print(f'ваш API-токен недействителен. Измените его на корректный в настройках (ошибка: {e})')
            break
        if result:
            print_result(result)
        else:
            print(f'По запросу "{text}" не найдено ни одного результата.')
            continue

        while True:
            try:
                address_num = input(
                    "Выберите номер необходимого вам адреса. Если подходящего адреса нет или вы хотите "
                    "вернуться, нажмите Enter.\n")
                if address_num == '':
                    break
                address_num = int(address_num)
                if not 0 < address_num < len(result) + 1:
                    print_result(result)
                    print(f"Введите число от 1 до {len(result)}.")
                    continue
            except ValueError as e:
                print_result(result)
                print(f"Введите целое число (ошибка {e}).")
                continue
            value, lat, lon = result[address_num - 1]['value'], \
                result[address_num - 1]['data']['geo_lat'], \
                result[address_num - 1]['data']['geo_lon']
            print(f'Координаты по адресу "{value}" [широта - долгота]:', lat, '-', lon)
            address_num = 0


def change_settings(db_name):
    while True:
        request = settings_menu()
        match request:
            case '1':
                lang = db.input_language()
                if lang:
                    db.Settings.set_parameter('language', lang)
            case '2':
                token = db.input_token()
                if token:
                    db.Settings.set_parameter('token', token)
            case '':
                break
            case _:
                print("Введите число или нажмите Enter для выхода.")


def menu():
    while True:
        request = start_menu()

        match request:
            case '1':
                get_request_from_dadata(db.Settings.get_parameter('token'), db.Settings.get_parameter('language'))
            case '2':
                change_settings(DB_PATH)
            case '3':
                db.Settings.view_settings()
            case '':
                break
            case _:
                print("Введите число или нажмите Enter для выхода.")


if __name__ == "__main__":
    print("Добро пожаловать в программу поиска точных географических координат по адресу с помощью сервиса DaData.")
    if not os.path.exists(DB_PATH):
        print('Необходимо инициализировать настройки программы. Для отмены нажмите Enter')
        db.create_settings_database(DB_PATH)
    db.Settings.set_parameters_from_db(DB_PATH)

    menu()
    db.Settings.set_parameters_to_db(DB_PATH)
    print('До свидания и хорошего дня!')
    time.sleep(3)
