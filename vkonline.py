from getpass import getpass
from sys import platform
from colorama import init, Fore
from random import randrange
from datetime import datetime
from pathlib import Path
import os
import requests
import json
import time

VK_API_VERSION = '5.123'
VK_API_OAUTH_URL = 'https://oauth.vk.com/token'
VK_API_METHODS_URL = 'https://api.vk.com/method/'

VK_APP_VKMESSENGER_ID = '5027722'
VK_APP_VKMESSENGER_SECRET = 'Skg1Tn1r2qEbbZIAJMx3'

ERROR = ''

def request_credentials():
    login = input('Введите логин: ')
    password = getpass('Введите пароль: ')

    return login, password

def api(url, params = {}):
    headers = {
        'Accept-Language': 'ru',
        'User-Agent': 'VKDesktopMessenger/5.2.3 (win32; 10.0.19042; x64)'
    }
    response = requests.get(url, params=params, headers=headers)
    return response

def start_online(token):
    if token == None or token == '':
        eprint('Для запуска онлайна требуется токен!')
        exit()

    iprint('Запуск онлайна...')
    vk_id, name, surname = get_vk_info(token)
    if vk_id == 0:
        eprint('Что-то пошло не так при запросе данных о странице.')
        exit()

    params = {
        'access_token': token,
        'lang': 'ru',
        'v': VK_API_VERSION
    }

    # 210 секунд = 3.5 минуты
    sleep_time = 210
    success_run = False
    while True:
        response = parse_api_response(api(VK_API_METHODS_URL + 'account.setOnline', params))
        res = json.loads(response.text)
        if res['response'] == 1:
            if success_run == False:
                success_run = True
                okprint('Онлайн успешно запущен для аккаунта id' + str(vk_id) + ' (' + name + ' ' + surname + ')!', log='d')
            dlog('Вызов метода account.setOnline прошёл успешно.')
        else:
            dlog('Произошла ошибка при вызове метода account.setOnline.')
            dlog(response.text)
        time.sleep(sleep_time + randrange(60))

def api_logIn(login, password):
    params = {
        'grant_type': 'password',
        'client_id': VK_APP_VKMESSENGER_ID,
        'client_secret': VK_APP_VKMESSENGER_SECRET,
        'username': login,
        'password': password,
        '2fa_supported': 1,
        'scope': 'offline',
        'v': VK_API_VERSION
    }
    response = parse_api_response(api(VK_API_OAUTH_URL, params))
    res = json.loads(response.text)
    if res['access_token']:
        okprint('Авторизация прошла успешно, токен получен!')
        start_online(res['access_token'])
    else:
        eprint('При авторизации что-то пошло не так. Ответ от сервера неизвестен.')
        wprint(response.text)

def parse_api_response(response):
    res = json.loads(response.text)
    if response.status_code != 200 or 'error' in res:
        return parse_api_error(response)
    elif response.status_code == 200:
        return response
    
    eprint('От сервера пришёл неизвестный скрипту ответ.', log='e')
    wprint(response.text, log='e')
    exit()

def get_vk_info(token):
    params = {
        'access_token': token,
        'v': VK_API_VERSION
    }

    response = parse_api_response(api(VK_API_METHODS_URL + 'users.get', params))
    res = json.loads(response.text)
    id = 0
    first_name = ''
    last_name = ''
    if 'response' in res:
        if 'id' in res['response'][0]:
            id = res['response'][0]['id']
            first_name = res['response'][0]['first_name']
            last_name = res['response'][0]['last_name']

    return id, first_name, last_name

def parse_api_error(response):
    global ERROR

    res = json.loads(response.text)
    if res['error']:
        error = res['error']
        if type(error) == dict:
            error_code = error['error_code']
            if error_code == 5:
                eprint('Авторизация не удалась.')
                if 'revoke access for this token' in error['error_msg']:
                    ERROR = 'Токен был отозван.'
                    run()
                elif 'invalid access_token' in error['error_msg']:
                    ERROR = 'Некорретный токен.'
                    run()
                else:
                    ERROR = error['error_msg']
                    run()
            else:
                unknown_server_error('error_code: ' + error_code + ', error_msg: ' + error['error_msg'])
        elif error == 'need_captcha':
            captcha_code = request_captcha(res['captcha_img'])
            return parse_api_response(api(response.url + '&captcha_sid=' + res['captcha_sid'] + '&captcha_key=' + captcha_code))
        elif error == 'invalid_client':
            error_type = res['error_type']
            if error_type == 'username_or_password_is_incorrect':
                ERROR = res['error_description']
                run()
            else:
                unknown_server_error(response.text)
        elif error == 'need_validation':
            validation_type = res['validation_type']
            if validation_type == '2fa_app':
                iprint('У вас включена двухфакторная авторизация, требуется подтверждение с помощью приложения для генерации кодов.')
                return auth_2fa(response, validation_type, res['phone_mask'])
            elif validation_type == '2fa_sms':
                iprint('У вас включена двухфакторная авторизация, требуется подтверждение через SMS.')
                return auth_2fa(response, validation_code, res['phone_mask'])
            else:
                unknown_server_error(response.text)
        else:
            unknown_server_error(response.text)

def unknown_server_error(text):
    eprint('Сервер ответил ошибкой, которую скрипт не может обработать.', log='e')
    wprint(text, log='e')
    exit()

def auth_2fa(response, validation_code, phone_mask):
    print('1. Ввести код')
    if validation_code == '2fa_app':
        print('2. Запросить код по СМС')
    elif validation_code == '2fa_sms':
        print('2. Повторно запросить код по СМС')
    else:
        eprint('Неизвестный тип подтверждения')
        exit()
    mode = input('Выберите вариант: ')
    if mode == '1':
        validation_code = input('Введите код: ')
        return parse_api_response(api(response.url + '&code=' + validation_code))
    elif mode == '2':
        iprint('Код будет выслан на номер ' + phone_mask)
        return parse_api_response(api(response.url + '&force_sms=1'))
    else:
        eprint('Неизвестный вариант')
        return auth_2fa(response, validation_code, phone_mask)

def request_captcha(captcha_img):
    wprint('Требуется ввод капчи!')
    iprint('Откройте капчу по ссылке ниже любым удобным для вас способом и введите в ответ код, изображённый на капче.')
    iprint('Ссылка на капчу: ' + captcha_img)
    return input('Введите код с капчи: ')

def eprint(text, log=False):
    logprint(Fore.RED + 'E: ', text, log)

def iprint(text, log=False):
    logprint(Fore.CYAN + 'I: ', text, log)

def wprint(text, log=False):
    logprint(Fore.YELLOW + 'W: ', text, log)

def okprint(text, log=False):
    logprint(Fore.GREEN + 'OK: ', text, log)

def logprint(prefix, text, log):
    print(prefix + text)
    if log == 'debug' or log == 'd':
        dlog(text)
    elif log == 'error' or log == 'e':
        elog(text)

def dlog(text):
    if platform == 'win32':
        filename = 'logs\\debug.log'
    else:
        filename = 'logs/debug.log'
    log(filename, text)

def elog(text):
    if platform == 'win32':
        filename = 'logs\\error.log'
    else:
        filename = 'logs/error.log'
    log(filename, text)

def log(filename, text):
    current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    text = '[' + current_time + '] ' + text + '\n'
    Path('logs').mkdir(exist_ok=True)
    with open(filename, 'a') as f:
        f.write(text)

def clear_screen():
    if platform == 'win32':
        os.system('cls')
    elif platform == 'linux':
        os.system('clear')

def check_credentials(login, password):
    global ERROR

    if login == '':
        ERROR = 'Логин не может быть пустым'
        return False
    if password == '':
        ERROR = 'Пароль не может быть пустым'
        return False
    return True

def run():
    global ERROR

    clear_screen()
    if ERROR != '':
        eprint(ERROR)
    print('1. Авторизация по логину и паролю')
    print('2. Авторизация по токену')
    mode = input('Выберите режим авторизации: ')
    if mode == '1':
        login, password = request_credentials()
        if not check_credentials(login, password):
            run()
        api_logIn(login, password)
    elif mode == '2':
        iprint('Обратите внимание, что при авторизации по токену онлайн будет работать от имени того приложения, через которое токен был получен!')
        token = input('Вставьте токен: ')
        start_online(token)
    else:
        ERROR = 'Неизвестный режим авторизации'
        run()

if __name__ == '__main__':
    init(autoreset=True)
    run()