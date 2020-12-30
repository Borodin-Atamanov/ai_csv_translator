from config.config import *
import csv
import sys
import sqlite3

con = sqlite3.connect(db['sqlite3file'])

with open(files['input_csv_file'], mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        #print(repr(row))
        if line_count == 0:
            print(repr(row))
            #print(f'Column names are {", ".join(row)}')
        #print(f'\t{row["name"]} works in the {row["department"]} department, and was born in {row["birthday month"]}.')
        #if line_count == 3:
            #print(repr(row))

        line_count += 1
    print(f'Processed {line_count} lines.')

sql_query = "select 1+1"
con.execute(sql_query)

#print(con.fetchall())

