import json

language = 'en'
translates = None

def set_language(lang):
    global language

    language = lang

def read_translates():
    global translates

    with open('languages.json', 'r', encoding='utf-8') as f:
        try:
            translates = json.loads(f.read())
        except json.JSONDecodeError as e:
            print('The translation file contains invalid JSON')
            exit()

def translate(text, dict = 'general'):
    if translates == None:
        read_translates()
    if language in translates:
        lang_dict = translates[language][dict]
        if text in lang_dict:
            return lang_dict[text]

    return text