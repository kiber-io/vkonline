# vkonline
Eternal online for VKontakte written in Python

### What is it?
The script of the eternal online for the famous social network VKontakte (https://vk.com).
Masquerades as the official VK Messenger app for Windows 10.

### How does it work?
The script repeats authorization requests and calls to the `account.setOnline` method in accordance with the way the official VK Messenger app does it.
Requests are sent every 4 minutes + a random number of seconds from 0 to 60. Random time calculation is necessary to avoid automatic requests being recognized by the VKontakte server.

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
    - Login and password authorization: the script requests a token with the scope=offline parameter, which allows you to get a token with almost no rights. All that the received token is capable of is getting general information about the page (for example, first and last name). There is NO access to messages (reading, sending) and other personal data.
    - Authorization by token: all responsibility rests with you. You cannot" take away " the rights from a previously received token. If you use a token with critical access rights (for example, messages), then I am not responsible for any further consequences. The script itself does not merge or save the token anywhere, but during operation, the token is stored in the process memory, and can also be seen in network requests (the script works via HTTPS).
- Support for two-factor authorization (SMS, call, code from the app to generate codes)
- Captcha support (only in manual mode, i.e. you will be given a link to the captcha, which you will need to open manually, and the script will request the code from the image)
- Easy translation into any language (the file `languages.json` and the variable `LANGUAGE` in the file header `vkonline.py`)

### Usage
1. Clone the repository
```
git clone https://github.com/kiber-io/vkonline
cd vkonline
```
2. Install the dependencies
    - Windows  
    `python -m pip install -r requirements.txt`
    - Linux, MacOs, Android  
    `python3 -m pip install -r requirements.txt`
3. Run the script
    - Windows  
    `python vkonline.py`
    - Linux, MacOs, Android  
    `python3 vkonline.py`