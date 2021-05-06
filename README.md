# vkonline
Eternal online for VK

### What is it?
A script for perpetual online, using data from the desktop application VK Messenger. Sends an online request every ±5 minutes (the time is calculated randomly to avoid recognition of automatic requests).

### Features
- Login and password authorization
- Security (the token is obtained with the scope=offline parameter, i.e. it does not have access to any personal data, only public data from the page)
- Support for two-factor authorization (SMS, call, code from the app)
- Captcha processing (in manual mode)
