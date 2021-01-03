from config.config import *

#Create backups dir (if not exists)
if not os.path.exists(files['backups_dir']): os.makedirs(files['backups_dir'])
#Backup BD
if (os.path.isfile(db['sqlite3file'])): shutil.move (db['sqlite3file'], files['backups_dir']+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+files['db_backup_filename_end'])

#Create new DataBase if it is not exists
if not os.path.exists(db['sqlite3file']): 
    #print('Файла нет,создаём')
    con = sqlite3.connect(db['sqlite3file'])
    cur = con.cursor()
    result = cur.execute("""
    CREATE TABLE `sentences` (
    `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    `original_id`   TEXT,
    `from`  TEXT,
    `to`    TEXT,
    `computed`  INTEGER
    );
    """)
    result = cur.execute("""
    CREATE TABLE `glossary` (
    `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    `from`  TEXT,
    `to`    TEXT
    );
    """)
    result = cur.execute("""
    CREATE TABLE `translation_cache` (
    `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    `from`  TEXT,
    `to`    TEXT,
    `created`   INTEGER
    );
    """)
    con.commit()
else:
    #Just make connection to db
    con = sqlite3.connect(db['sqlite3file'])
    cur = con.cursor()


#Read data from CSV and load it to SQLite3-database
with open(files['input_csv_file'], mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    line_count = 0
    for row in csv_reader:
        computed = int(time.time())
        result = cur.execute("insert into `sentences` (`original_id`, `from`) values (?, ?)", (row[0], row[1]))
        line_count += 1
        if line_count > 1000: break;
    print(f'Processed {line_count} lines.')
    con.commit()
    
#TODO Read data from glossary CSV and load it to SQLite3-database


