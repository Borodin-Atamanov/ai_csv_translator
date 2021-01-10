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

files = {
    "input_csv_file": 'input/tm.csv',
    "backups_dir": 'backups/',
    "db_backup_filename_end": '.sqlite3db',
    
}
db = {
    "sqlite3file": 'main.sqlite3db',
}
