from config.config import *

from pprint import pprint #Для отладки

con = sqlite3.connect(db['sqlite3file'])
cur = con.cursor()

#walk on untranslated sentences in DB, sent it to parser
cur.execute('SELECT * FROM `sentences` WHERE `computed` IS NULL  ORDER BY `id` DESC')
#cur.execute('SELECT * FROM `sentences` WHERE `computed` IS NULL  ORDER BY `id` ASC')

while True:
    row = cur.fetchone()
    if row == None:
        break
    id, original_id, from_sent = row[0], row[1], row[2]
    print(from_sent)
    #create parser object
    sent = SentenceParser(from_sent)
    pprint(repr(sent))
    translated_sentence = sent.get_translated()
    #TODO save translated sentence to database
    time.sleep(0.4)

#sent = SentenceParser()
