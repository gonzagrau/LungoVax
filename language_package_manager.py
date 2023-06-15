import json

ES_PACK_PATH = 'lang_es.json'
EN_PACK_PATH = 'lang_en.json'

def get_system_language():
    from sys import platform
    import locale
    lang = locale.getlocale()[0]
    if 'es' in lang or 'spanish' in lang.lower():
        return 'es'
    elif 'en' in lang or 'english' in lang.lower():
        return 'en'
    else:
        return 'en'

def get_lang_package(lang: None|str = None):
    if lang is None:
        lang = get_system_language()
    match lang:
        case 'en':
            lang_path = EN_PACK_PATH
        case 'es':
            lang_path = ES_PACK_PATH
        case _:
            raise NotImplementedError(f'Language {lang} is nor suported.')
    with open(lang_path, 'r', encoding='utf-8') as f:
        return json.load(f)
