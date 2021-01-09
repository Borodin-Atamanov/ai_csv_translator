import csv
import sys
import sqlite3
import time
import datetime
import shutil
import os
import pprint

#Класс парсинга фраз перед и после перевода
from sentence_parser import SentenceParser
#Класс работы с базой
from singleton_db import SingletonDB

files = {
    "input_csv_file": 'input/tm.csv',
    "backups_dir": 'backups/',
    "db_backup_filename_end": '.sqlite3db',
    
}
db = {
    "sqlite3file": 'main.sqlite3db',
}
