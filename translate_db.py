from config.config import *
#from myclass import MyClass
#Для отладки
from pprint import pprint


con = sqlite3.connect(db['sqlite3file'])
cur = con.cursor()

#sent = SentenceParser()

#walk on untranslated sentences in DB, sent it to parser
#ToDo добиться работы с условием 
cur.execute('SELECT * FROM `sentences` WHERE `computed` IS NULL  ORDER BY `id` DESC')
#cur.execute('SELECT * FROM `sentences` ORDER BY `id` DESC')
#cur.execute('SELECT * FROM `sentences` ORDER BY `id` ASC')

#ToDo 
while True:
    row = cur.fetchone()
    if row == None:
        break
    id, original_id, from_sent = row[0], row[1], row[2]
    print(from_sent)
    sent = SentenceParser(from_sent)
    pprint(repr(sent))
    time.sleep(0.4)

#sent = SentenceParser()