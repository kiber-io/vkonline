# vkonline
[![CodeQL](https://github.com/kiber-io/vkonline/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/kiber-io/vkonline/actions/workflows/codeql-analysis.yml)

Eternal online for VKontakte, written in Python

### What is it?
The script of the eternal online for the well-known social network VKontakte (https://vk.com).
It disguises itself as the official VK Messenger application for Windows 10.

### How does it work?
The script repeats authorization requests and calls to the `account.setOnline` method in accordance with the way the official VK Messenger application does it.
Requests are sent every 3.5 minutes + a random number of seconds from 0 to 60. Random time calculation is necessary to avoid automatic requests being recognized by the VKontakte server.

### Requirements and dependencies
- Python >= 3.5
- certifi (tested on version 2020.12.5)
- chardet (tested on version 4.0.0)
- colorama (tested on version 0.4.4)
- idna (tested on version 2.10)
- requests (tested on version 2.25.1)
- urllib3 (tested on version 1.26.5)

### Features
- Cross-platform (Windows, Linux, macOS, Android)
- Login and password authorization
- Authorization by token
- Security
-Login and password authorization: the script requests a token with the scope=offline parameter, which allows you to get a token with almost no rights. All that the received token is capable of is getting general information about the page (for example, first and last name). There is NO access to messages (reading, sending), etc.personal data.
    - Authorization by token: all responsibility is assigned to you. You cannot "take away" the rights from a previously received token. If you use a token with critical access rights (for example, messages), then I am not responsible for further consequences. The script itself does not merge anywhere and does not save the token, however, during operation, the token is stored in the process memory, and can also be visible in network requests (the script works via HTTPS).
- Support for two-factor authorization (SMS, call, code from the application for generating codes)
- Captcha support (only in manual mode, i.e. the script will give you a link to the captcha, which will need to be opened manually, and will also request the code that will need to be entered from this very captcha)
- Easy translation into any language (the `languages.json` file and the `LANGUAGE` variable in the file header `vkonline.py`)

### Installation
1. Clone the repository
```
git clone --recurse-submodules https://github.com/kiber-io/vkonline
cd vkonline
```
2. It is recommended to perform all further actions in the Python virtual environment.

    - Windows-style  
    ```
    python -m pip venv env
    etc\Scripts\activate.bat
    ```  
    - Unix-style  
    ```
    python3 -m pip venv env
    source env/bin/activate
    ```  
3. Install the dependencies  

    - Windows-style  
    ```
    python -m pip install -r requirements.txt
    ```
    - Unix-style  
    ```
    python3 -m pip install -r requirements.txt
    ```
### Launch
1. The most difficult part of the manual  

    - Windows-style  
    ```
    python vkonline.py
    ```
    - Unix-style  
    ```
    python3 vkonline.py
    ```
