from config.config import *
import csv
import sys
import sqlite3
import time

con = sqlite3.connect(db['sqlite3file'])

#Read data from CSV and save it to SQLite3-database
with open(files['input_csv_file'], mode='r') as csv_file:
    csv_reader = csv.reader(csv_file)
    line_count = 0
    for row in csv_reader:
        computed = int(time.time())
        #ToDo исправить: должно добавляться в базу данных, а сейчас - не добавляется почему-то
        result = con.execute("insert into 'sentences' ('original_id', 'from', 'to', 'computed') values (?, ?, ?, ?)", (row[0], row[1], row[2], computed))
        print(result)
        con.commit()
        #ToDo добавить try-catch блок для запросов к БД
        #Отловить результат выполнения запроса к БД

        if line_count == 10: break;

        #print(f'Column names are {", ".join(row)}')
        #print(f'\t{row["name"]} works in the {row["department"]} department, and was born in {row["birthday month"]}.')
        #if line_count == 3:
        #print(repr(row))

        line_count += 1
    print(f'Processed {line_count} lines.')

#sql_query = "select 1+1"
#con.execute(sql_query)

#print(repr(con));

