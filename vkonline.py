from getpass import getpass
from sys import platform
from random import randrange
import os
import requests
import json
import time
import signal

IS_MODULE = __name__ != '__main__'

if not IS_MODULE:
    from simplePyLog import simplePyLog
    from simplePyLocale import simplePyLocale
else:
    from .simplePyLog import simplePyLog
    from .simplePyLocale import simplePyLocale

############################ YOU CAN CHANGE IT ####################################
# The language in which the script will output its messages and write to the log
# The supported languages can be viewed in the languages.json file
LANGUAGE = 'ru'
# The language in which the VK server will respond. For what? I want so
LANGUAGE_VK = 'ru'

LANGUAGE_FILE = 'languages.json'
###################################################################################

############## DON'T CHANGE IT IF YOU DON'T KNOW WHAT ARE YOU DOING ###############
VK_API_VERSION = '5.123'
VK_API_OAUTH_URL = 'https://oauth.vk.com/token'
VK_API_METHODS_URL = 'https://api.vk.com/method/'
VK_APP_VKMESSENGER_ID = '5027722'
VK_APP_VKMESSENGER_SECRET = 'Skg1Tn1r2qEbbZIAJMx3'

ERROR = ''

_ = simplePyLocale.translate

###################################################################################

################################# DEBUG ###########################################
DEBUG = False
###################################################################################

def signal_handler(sig, frame):
    print()
    simplePyLog.iprint(_('bye_bye'))
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

def request_credentials():
    login = input(_('enter_login'))
    simplePyLog.iprint(_('password_not_visible'))
    password = getpass(_('enter_password'))

    return login, password

def api(url, params = {}):
    success_request = False
    headers = {
        'Accept-Language': LANGUAGE_VK,
        'User-Agent': 'VKDesktopMessenger/5.2.3 (win32; 10.0.19042; x64)'
    }
    if DEBUG:
        simplePyLog.netlog(_('log_request', 'debug').format(url=url, params=json.dumps(params)))
    while success_request == False:
        try:
            response = requests.get(url, params=params, headers=headers)
            success_request = True
        except Exception as e:
            simplePyLog.elog(_('network_error_log').format(error=e))
            retry = 60
            simplePyLog.eprint(_('network_error_retry').format(seconds=retry))
            time.sleep(retry)
    if DEBUG:
        simplePyLog.netlog(_('log_response', 'debug').format(response=response.text))
    return response

def start_online(token):
    if token == None or token == '':
        simplePyLog.eprint(_('online_need_token'))
        exit()

    simplePyLog.iprint(_('start_online'))
    vk_id, name, surname = get_vk_info(token)
    if vk_id == 0:
        simplePyLog.eprint(_('error_loading_vk_info'))
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
        if 'response' in res:
            if res['response'] == 1:
                if success_run == False:
                    success_run = True
                    simplePyLog.okprint(_('success_online_started').format(id=vk_id, name=name, surname=surname), log='d')
                simplePyLog.dlog(_('success_method_call').format(method='account.setOnline'))
            else:
                simplePyLog.dlog(_('error_method_call').format(method='account.setOnline'))
                simplePyLog.dlog(response.text)
        sleep_time_new = sleep_time + randrange(60)
        if DEBUG:
            simplePyLog.dlog(_('sleep_time', 'debug').format(seconds=sleep_time_new))
        time.sleep(sleep_time_new)
        if DEBUG:
            simplePyLog.dlog(_('sleep_time_end', 'debug'))

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
    if not IS_MODULE:
        if res['access_token']:
            simplePyLog.okprint(_('success_authorization'))
            start_online(res['access_token'])
        else:
            simplePyLog.eprint(_('error_authorization_unknown_error'))
            simplePyLog.wprint(response.text)
    else:
        return res

def parse_api_response(response):
    res = json.loads(response.text)
    if response.status_code != 200 or 'error' in res:
        return parse_api_error(response)
    elif response.status_code == 200:
        return response
    
    simplePyLog.eprint(_('error_unknown_server_response'), log='e')
    simplePyLog.wprint(response.text, log='e')
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
                simplePyLog.eprint(_('error_authorization'))
                if 'revoke access for this token' in error['error_msg']:
                    ERROR = _('error_token_revoked')
                    run()
                elif 'invalid access_token' in error['error_msg']:
                    ERROR = _('error_token_incorrect')
                    run()
                else:
                    ERROR = error['error_msg']
                    run()
            else:
                simplePyLog.eprint(_('error_unknown_server_error'), log='e')
                simplePyLog.wprint('error_code: {error_code}, error_msg: {error_msg}'.format(error_code=error_code, error_msg=error['error_msg']), log='e')
                return response
        elif error == 'need_captcha':
            captcha_code = request_captcha(res['captcha_img'])
            return parse_api_response(api(response.url + '&captcha_sid=' + res['captcha_sid'] + '&captcha_key=' + captcha_code))
        elif error == 'invalid_client':
            error_type = res['error_type']
            if error_type == 'username_or_password_is_incorrect':
                ERROR = res['error_description']
                run()
            else:
                return unknown_server_error(response.text)
        elif error == 'need_validation':
            validation_type = res['validation_type']
            if validation_type == '2fa_app':
                simplePyLog.iprint(_('error_2fa_app'))
                return auth_2fa(response, validation_type, res['phone_mask'])
            elif validation_type == '2fa_sms':
                simplePyLog.iprint(_('error_2fa_sms'))
                return auth_2fa(response, validation_type, res['phone_mask'])
            else:
                return unknown_server_error(response.text)
        else:
            return unknown_server_error(response.text)

def unknown_server_error(text):
    simplePyLog.eprint(_('error_unknown_server_error'), log='e')
    simplePyLog.wprint(text, log='e')
    return {'error': text}

def auth_2fa(response, validation_type, phone_mask):
    print('1. {text}'.format(text=_('enter_code')))
    if validation_type == '2fa_app':
        print('2. {text}'.format(text=_('request_code_sms')))
    elif validation_type == '2fa_sms':
        print('2. {text}'.format(text=_('retry_request_code_sms')))
    else:
        simplePyLog.eprint(_('error_unknown_validation_type'))
        exit()
    mode = input(_('choose_variant'))
    if mode == '1':
        validation_code = input(_('please_enter_code'))
        return parse_api_response(api(response.url + '&code=' + validation_code))
    elif mode == '2':
        simplePyLog.iprint(_('code_send_to_phone').format(phone_mask=phone_mask))
        return parse_api_response(api(response.url + '&force_sms=1'))
    else:
        simplePyLog.eprint(_('error_unknown_variant'))
        return auth_2fa(response, validation_type, phone_mask)

def request_captcha(captcha_img):
    simplePyLog.wprint(_('error_need_captcha'))
    simplePyLog.iprint(_('please_open_captcha'))
    simplePyLog.iprint(_('captcha_url').format(captcha_img=captcha_img))
    return input(_('enter_code_captcha'))

def clear_screen():
    if platform == 'win32':
        os.system('cls')
    elif platform == 'linux':
        os.system('clear')

def check_credentials(login, password):
    global ERROR

    if login == '':
        ERROR = _('error_login_empty')
        return False
    if password == '':
        ERROR = _('error_password_empty')
        return False
    return True

def run():
    global ERROR

    clear_screen()
    if ERROR != '':
        simplePyLog.eprint(ERROR)
    print('1. {text}'.format(text=_('auth_login_password')))
    print('2. {text}'.format(text=_('auth_token')))
    mode = input(_('choose_auth_mode'))
    if mode == '1':
        login, password = request_credentials()
        if not check_credentials(login, password):
            run()
        api_logIn(login, password)
    elif mode == '2':
        simplePyLog.iprint(_('auth_token_warn'))
        token = input(_('enter_token'))
        start_online(token)
    else:
        ERROR = _('error_unknown_auth_type')
        run()

simplePyLocale.set_language(LANGUAGE)
simplePyLocale.set_language_file(LANGUAGE_FILE)
simplePyLog.set_regex_replacing({
    r'("(username|password|access_token)":\s?)".*?"': r'\g<1>"ooops_hidden"',
    r'((username|password|access_token)=).*?(?=[&\s])': r'\g<1>ooops_hidden'
})

if not IS_MODULE:
    run()
