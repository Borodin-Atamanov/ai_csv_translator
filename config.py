#import sys
#import sqlite3
#import time
#import pprint

#Секретные ключи для платного перевода
from config_secret_keys import config_secret_keys

#Класс парсинга фраз перед и после перевода
#from SentenceParser import SentenceParser
#Класс работы с базой
#from SingletonDB import SingletonDB
#Класс обращения к службам онлайн-перевода через платный API
#from TranslatorOnline import TranslatorOnline
#Класс локального кеширования полученных переводов, чтобы лишний раз не платить
#from TranslationCacher import TranslationCacher

config = {
    'files':
    {
        #Входящий файл, откуда происходит загрузка в базу данных
        "input_csv_file": 'input.csv',
        #Путь для бекапов базы данных
        "backups_dir": 'backups/',
        #Постфикс к имени файла бекапов баз данных
        "db_backup_filename_end": '.sqlite3db',
    },

    #База данных
    'db':
    {
        #Имя файла базы данных
        "sqlite3file": 'main.sqlite3db',
    },

    #Настройки перевода
    'translation':
    {
        #Символ, использующийся для перевода, который не влияет на качество перевода,
        #Такие символы временно заменяют собой теги перед отправкой на онлайн перевод
        'safety_for_translation_sign':  '#',
        #Какие символы добавлять вокруг safety_for_translation_sign при замене тегов (этот символ останется в результирующем переводе!)
        #'add_this_char_around_safety_for_translation_sign': ' ',
        'add_this_char_around_safety_for_translation_sign': '',
        #Минимальное количество символов, временно кодирующее один тег
        'minimum_safety_for_translation_chars':  3,
        #change HTML-entities to UTF8-chars
        'change_html_entities_to_utf8_chars': False,

        #Настройки машинного перевода через API
        #Код исходного языка
        "sourceLanguageCode": "ru",
        #Код целевого языка
        "targetLanguageCode": "en",
        #Формат текста
        "format": "HTML",
    },

    #Секретные ключи для доступа к платному переводу, импортируются из файла config_secret_keys.py
    'secret_keys':
    {
        'yandex':
        {
            "folderId": None,
            "Api-Key": None,
        },
    },
}

#Регулярные выражения для нахождения тегов (которые не отправляются на перевод, чтобы не перевод их не испортил
config['regex_tags'] = [ \
        #HTML-сущности цифровые
        r'\s*&#\d{,7};\s*',
        #HTML-сущности буквенные
        r'\s*&[#0-9a-zA-Z]{,7};\s*',
        #HTML-сущности буквенные
        r'\s*&[#0-9a-zA-Z]{,7};\s*',
        #\n\r\t \[любая латинская буква]
        r'\s*\\[a-zA-Z]{1}\s*',
        #Все %%-теги от % до % и пробельные символы до и после тега
        #Между %% не может быть кириллица!
        #Длина строки между %% не ограничена
        r'\s*%[^А-я]*%\s*',
        #{|} - пустой половой тег
        r'\s*\{\|\}\s*',
        #(%TAG%)
        r'\s*\(%[^А-я]*%\)\s*',
        #Все HTML-теги: от < до > и пробельные символы до и после тега
        r'\s*<.*?>\s*',
        #%1$s %3$d
        r'\s*\%\d{1}\$[a-zA-Z-]{1}\s*',
        #Слова латиницей с подчёркиваниями и, возможно тире: начинается с фразы, включающей буквы, подчёркивание, тире, потом подчёркивание, потом фраза без подчёркивания
        #Flower-light_3-4_red
        r'\s*[_0-9a-zA-Z-]{1,}_[0-9a-zA-Z-]{1,}\s*',
        #Slovo_SlovoEsche
        r'\s*[0-9a-zA-Z-]{1,}_[0-9a-zA-Z-]{1,}\s*',
        #id=1022
        #Работает ошибочно! Добавляет чисто цифры в теги!
        #r'\s*[0-9a-zA-Z\=\#]{3,}\s*',

        # "переводобезопасный символ #" (он есть в конфигурации) -
        #Если этот символ вдруг встретиться в изначальном тексте - то будет бережно сохранён как тег
        r'\s*\\'+config['translation']['safety_for_translation_sign']+'*\s*',
    ]

#"Половые" теги вида "Все посчита{л|ла}? Сначала скажиме мне, сколько квадратов ты наш{ел|ла} в этой фигуре?"
config['sex_tags'] = { \
        #Символ начала
        'start_char'    :   '{',
        #Символ средины
        'middle_char'    :   '|',
        #Символ конца
        'end_char'    :   '}',
        #Сохранять ли пустой половой тег в том месте текста, где он должен быть?
        #'save_empty_sex_tags'   : True,
        'save_empty_sex_tags'   : False,
    }

#импортировать настройки перевода из другого файла из соображений безопасности
config['secret_keys'] = config_secret_keys

#print(config)
