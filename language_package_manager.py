import json


EN_PACK_PATH = r'./assets/language_packages/lang_en.json'
ES_PACK_PATH = r'./assets/language_packages/lang_es.json'
LANG_LIST_SF = ['en', 'es']
LANG_DICTIONARY_PATHS = {'en': EN_PACK_PATH,
                         'es': ES_PACK_PATH}


def get_system_language():
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
    if lang not in LANG_LIST_SF:
        raise NotImplementedError(f'Language {lang} is nor supported.')
    lang_path = LANG_DICTIONARY_PATHS[lang]
    with open(lang_path, 'r', encoding='utf-8') as f:
        return json.load(f)
