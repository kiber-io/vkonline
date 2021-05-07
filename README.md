# vkonline
Eternal online for VK

### What is it?
A script for perpetual online, using data from the desktop application VK Messenger. Sends an online request every ±5 minutes (the time is calculated randomly to avoid recognition of automatic requests).

### Features
- Cross-platform (Windows, Linux, macOS, Android)
- Login and password authorization
- Token authorization
- Security
    - When logging in with a username and password, the script receives a token with the scope=offline parameter, so access is only available to general information about the user, such as first and last name, etc.
    - When logging in with a token, you are solely responsible, since you cannot "take away" the rights from the token. Pay close attention to what rights you use the token with.
- Support for two-factor authorization (SMS, call, code from the app)
- Captcha processing (in manual mode)
