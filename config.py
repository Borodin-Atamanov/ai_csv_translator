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
        "input_csv_file": 'input/tm.csv',
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
        #Минимальное количество символов, временно кодирующее один тег
        'minimum_safety_for_translation_chars':  3,

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
#TODO импортировать настройки перевода из другого файла из соображений безопасности
config['secret_keys'] = config_secret_keys

#print(config)
