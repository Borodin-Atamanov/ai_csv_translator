import os
import csv
import shutil
import datetime
from config import config

#Класс работы с базой
from SingletonDB import SingletonDB

#Create backups dir (if not exists)
if not os.path.exists(config['files']['backups_dir']):
    os.makedirs(config['files']['backups_dir'])
#Backup BD
if (os.path.isfile(config['db']['sqlite3file'])):
    #Move all DB to backups
    shutil.move (config['db']['sqlite3file'], config['files']['backups_dir']+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+config['files']['db_backup_filename_end'])

#Create new object to communicate with database
db1 = SingletonDB()
#Open connection to sqlite3 database file
db1.open(config['db']['sqlite3file'])
#pprint(dir(db1))
#print(dir(db1))
#print(db1)

#Read data from CSV and load it to SQLite3-database
with open(config['files']['input_csv_file'], mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    line_count = 0
    for row in csv_reader:
        db1.insert_new_untranslated_sentence(row[0], row[1])
        line_count += 1
        #if line_count > 1000:            break;
    print(f'Processed {line_count} lines.')
    db1.commit()

#TODO Read data from glossary CSV and load it to SQLite3-database
print(db1.__dict__)

