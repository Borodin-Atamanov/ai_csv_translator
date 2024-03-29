import os
import sqlite3
import datetime

class SingletonDB(object):
    "Singleton Database class used for access database from any point of application"
    #Имя файла базы
    db_file = None
    #Connection to database
    #con = None
    #Cursor
    #cur = None

    def __new__(cls):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance

    def open(self, db_file):
        "Open connection to database"
        self.db_file = db_file

        all_new_tables_needed = 0
        if not os.path.exists(self.db_file):
            #Файла нет, создаём все таблицы в базе данных
            all_new_tables_needed = 1

        self.con = sqlite3.connect(self.db_file, timeout=5)
        #Set row result to dict instead of tuple - very useful and important for this application
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()
        #self.continue_with_next_row = ''

        if all_new_tables_needed == 1:
            #Файла нет, создаём все таблицы в базе данных
            self.create_all_new_tables()
        return True

    def execute(self, query, arg=None):
        "Execute SQL query"
        if arg is not None:
            print(' SQL Arguments: ' + repr(arg))
            result = self.cur.execute(query, arg)
        else:
            result = self.cur.execute(query)
        self.rowcount = self.cur.rowcount
        self.lastrowid = self.cur.lastrowid
        self.description = self.cur.description
        return result

    def commit(self):
        "Commit all changes to database"
        return self.con.commit()

    def insert_new_untranslated_sentence(self, original_id, text):
        "insert new untranslated sentence to sentences table. original_id and text in arguments"
        #print(original_id, text)
        #result = self.cur.execute("insert into `sentences` (`original_id`, `from`) values (?, ?)", (original_id, text))
        result = self.execute("insert into `sentences` (`original_id`, `from`) values (?, ?)", (original_id, text))
        return result

    def get_next_untranslated_sentence(self):
        "get next sentence where computed is null"
        #walk on untranslated sentences
        result = self.execute('SELECT * FROM `sentences` WHERE `computed` IS NULL AND `error` < 1 ORDER BY `id` ASC')
        return self.get_row()

    def save_translated_sentence(self, values_in_dict):
        "Save translated sentence to database. Arguments: dict('id' - row id, 'to' - translated text"
        #result = self.execute('SELECT * FROM `sentences` WHERE `computed` IS NULL ORDER BY `id` DESC')
        values_in_dict['computed'] = int(datetime.datetime.now().timestamp())
        values_in_dict['error'] = values_in_dict.get('error', 0)
        result = self.execute('''UPDATE `sentences` SET `to`=:to, `computed`=:computed, `error`=:error WHERE `id`=:id LIMIT 1''', values_in_dict)
        self.commit()
        return result

    def save_to_cache(self, values_in_dict):
        "Save translated sentence to database. Arguments: dict('id' - row id, 'from' - input text, 'to' - translated text"
        values_in_dict['computed'] = int(datetime.datetime.now().timestamp())
        result = self.execute('''REPLACE INTO `translation_cache` (`from`, `to`, `computed`) VALUES (:from, :to, :computed); ''', values_in_dict)
        self.commit()
        return result

    def get_from_cache(self, values_in_dict):
        "get sentence from cache"
        #walk on untranslated sentences
        result = self.execute('SELECT * FROM `translation_cache` WHERE `from`=:from ORDER BY `computed` DESC LIMIT 1', values_in_dict)
        return self.get_row()

    def get_row(self):
        "Fetch one row and return it. None also can be returned"
        self.last_row = self.cur.fetchone()
        if self.last_row is None:
            return None
        #create dict with keys
        row_dict = dict(zip(self.last_row.keys(), self.last_row))
        return row_dict

    def create_all_new_tables(self):
        "Create all tables in new database"
        result = self.cur.execute("""
        CREATE TABLE `sentences` (
        `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        `original_id`   TEXT,
        `from`  TEXT,
        `to`    TEXT,
        `computed`  INTEGER,
        `error`  INTEGER DEFAULT 0 NOT NULL
        );
        """)
        result = self.cur.execute("""
        CREATE TABLE `glossary` (
        `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        `from`  TEXT,
        `to`    TEXT
        );
        """)
        result = self.cur.execute("""
        CREATE TABLE `translation_cache` (
        `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        `from`  TEXT,
        `to`    TEXT,
        `computed`   INTEGER
        );
        """)
        result = self.cur.execute("""
        CREATE INDEX from_cache_text
        ON translation_cache(`from`);
        """)
        return self.commit()

