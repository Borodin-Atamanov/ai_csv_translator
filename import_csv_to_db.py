from config import *

#Create backups dir (if not exists)
if not os.path.exists(files['backups_dir']): os.makedirs(files['backups_dir'])
#Backup BD
if (os.path.isfile(db['sqlite3file'])): shutil.move (db['sqlite3file'], files['backups_dir']+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+files['db_backup_filename_end'])

#Create new object to communicate with database
db1 = SingletonDB()
#Open connection to sqlite3 database file
db1.open(db['sqlite3file'])
#pprint(dir(db1))
#print(dir(db1))
#print(db1)

#Read data from CSV and load it to SQLite3-database
with open(files['input_csv_file'], mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    line_count = 0
    for row in csv_reader:
        db1.insert_new_untranslated_sentence(row[0], row[1])
        line_count += 1
        if line_count > 1000:
            break;
    print(f'Processed {line_count} lines.')
    db1.commit()

#TODO Read data from glossary CSV and load it to SQLite3-database
print(db1.__dict__)
