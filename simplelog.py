from colorama import init, Fore
from pathlib import Path
from sys import platform
from datetime import datetime
import re

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

def netlog(text):
    if platform == 'win32':
        filename = 'logs\\network.log'
    else:
        filename = 'logs/network.log'
    text = re.sub(
        r'("access_token":\s?)".*?"',
        r'\g<1>"hidden :P"',
        re.sub(
            r'("username":\s?)".*?"',
            r'\g<1>"hidden :P"',
                re.sub(
                    r'("password":\s?)".*?"',
                    r'\g<1>"hidden :P"',
                    text
                )
        )
    )
    log(filename, text)

def elog(text):
    if platform == 'win32':
        filename = 'logs\\error.log'
    else:
        filename = 'logs/error.log'
    log(filename, text)

def log(filename, text):
    current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    text = '[' + current_time + '] ' + text + '\n'
    Path('logs').mkdir(exist_ok=True)
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(text)

init(autoreset=True)