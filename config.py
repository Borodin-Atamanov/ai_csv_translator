import csv
import sys
import sqlite3
import time
import datetime
import shutil
import os
#import pprint

#Класс парсинга фраз перед и после перевода
from SentenceParser import SentenceParser
#Класс работы с базой
from SingletonDB import SingletonDB
#Класс обращения к службам онлайн-перевода через платный API
from TranslatorOnline import TranslatorOnline
#Класс локального кеширования полученных переводов, чтобы лишний раз не платить
from TranslationCacher import TranslationCacher

config = {
    'files':
    {
        "input_csv_file": 'input/tm.csv',
        "backups_dir": 'backups/',
        "db_backup_filename_end": '.sqlite3db',
    },
    'db':
    {
        "sqlite3file": 'main.sqlite3db',
    },
    'translation':
    {
        #Символ, использующийся для перевода, который не влияет на качество перевода,
        #Такие символы временно заменяют собой теги перед отправкой на онлайн перевод
        'safety_for_translation_sign':  '#',
        #Минимальное количество символов, временно кодирующее один тег
        'minimum_safety_for_translation_chars':  3,
    }
}
