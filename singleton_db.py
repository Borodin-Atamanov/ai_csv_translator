import os
import sqlite3

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
        #Create new DataBase if it is not exists
        if not os.path.exists(self.db_file): 
            #Файла нет,создаём
            self.con = sqlite3.connect(self.db_file)
            self.cur = self.con.cursor()
            self.create_all_new_tables()
        else:
            #Just make connection to db
            self.con = sqlite3.connect(self.db_file)
            self.cur = self.con.cursor()
        return True

    def commit(self):
        "Commit all changes to database"
        return self.con.commit()

    def insert_new_untranslated_sentence(self, original_id, text):
        "insert_new_untranslated_sentence to sentences table. original_id and text in arguments"
        print(original_id, text)
        result = self.cur.execute("insert into `sentences` (`original_id`, `from`) values (?, ?)", (original_id, text))
        print(result)
        return result

    def create_all_new_tables(self):
        "Create all tables in new database"
        result = self.cur.execute("""
        CREATE TABLE `sentences` (
        `id`    INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
        `original_id`   TEXT,
        `from`  TEXT,
        `to`    TEXT,
        `computed`  INTEGER
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
        `created`   INTEGER
        );
        """)
        return self.commit()
    
