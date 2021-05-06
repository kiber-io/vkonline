from getpass import getpass
from sys import platform
from colorama import init, Fore
import os
import requests
import json

VK_API_VERSION = '5.123'
VK_API_OAUTH_URL = 'https://oauth.vk.com/token'
VK_API_METHODS_URL = 'https://api.vk.com/method/'

ERROR = ''

def request_credentials():
    login = input('Введите логин: ')
    password = getpass('Введите пароль: ')

    return login, password

def api(url, params = {}):
    headers = {
        'Accept-Language': 'en',
        'User-Agent': 'VKDesktopMessenger/5.2.3 (win32; 10.0.19042; x64)'
    }
    response = requests.get(url, params=params, headers=headers)
    return response

def api_logIn(login, password):
    params = {
        'grant_type': 'password',
        'client_id': '5027722',
        'client_secret': 'Skg1Tn1r2qEbbZIAJMx3',
        'username': login,
        'password': password,
        '2fa_supported': 1,
        'scope': 'offline',
        'v': VK_API_VERSION
    }
    response = parse_api_response(api(VK_API_OAUTH_URL, params))

def parse_api_response(response):
    if response.status_code != 200:
        parse_api_error(response)
        return
    
    eprint('От сервера пришёл неизвестный скрипту ответ.')
    wprint(response.text)

def parse_api_error(response):
    res = json.loads(response.text)
    if res['error']:
        error = res['error']
        if error == 'need_captcha':
            captcha_code = request_captcha(res['captcha_img'])
            return api(response.url + '&captcha_sid=' + res['captcha_sid'] + '&captcha_key=' + captcha_code)
        else:
            eprint('Сервер ответил ошибкой, которую скрипт не может обработать.')
            wprint(response.text)
            exit()

def request_captcha(captcha_img):
    wprint('Требуется ввод капчи!')
    iprint('Откройте капчу по ссылке ниже любым удобным для вас способом и введите в ответ код, изображённый на капче.')
    iprint('Ссылка на капчу: ' + captcha_img)
    return input('Введите код с капчи: ')

def eprint(text):
    print(Fore.RED + 'E: ' + text)

def iprint(text):
    print(Fore.CYAN + 'I: ' + text)

def wprint(text):
    print(Fore.YELLOW + 'W: ' + text)

def clear_screen():
    if platform == 'win32':
        os.system('cls')
    elif platform == 'linux':
        os.system('clear')

def run():
    global ERROR

    clear_screen()
    if ERROR != '':
        eprint(ERROR)
    login, password = request_credentials()
    if login == '':
        ERROR = 'Логин не может быть пустым'
        run()
    if password == '':
        ERROR = 'Пароль не может быть пустым'
        run()
    api_logIn(login, password)

if __name__ == '__main__':
    init(autoreset=True)
    run()