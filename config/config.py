import csv
import sys
import sqlite3
import time
import datetime
import shutil
import os

#Класс парсинга фраз перед и после перевода
from sentence_parser import SentenceParser

files = {
    "input_csv_file": 'input/tm.csv',
    "backups_dir": 'backups/',
    "db_backup_filename_end": '.sqlite3db',
    
}
db = {
    "sqlite3file": 'db/main.sqlite3db',
}
