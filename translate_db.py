from config import *

from pprint import pprint #Для отладки

con = sqlite3.connect(db['sqlite3file'])
cur = con.cursor()

#TODO использовать объект работы с БД для получения каждой следующей записи для перевода из базы
#walk on untranslated sentences in DB, sent it to parser
cur.execute('SELECT * FROM `sentences` WHERE `computed` IS NULL ORDER BY `id` DESC')
#cur.execute('SELECT * FROM `sentences` WHERE `computed` IS NULL ORDER BY `id` ASC')

#TODO получаем глоссарий из базы в виде словаря
glosary = dict()

while true:
    row = cur.fetchone()
    #TODO Получить следующую запись для перевода от объекта DB в цикле пока не кончатся записи
    if row == None:
        break
    id, original_id, from_sent = row[0], row[1], row[2]
    print(from_sent)
    #create parser object
    sent = SentenceParser(from_sent)

    pprint(vars(sent))
    #Производим перевод, передаём глоссарий в аргументах
    translated_sentence = sent.get_translated(glosary)
    #TODO перевод записывается обратно в базу, делается отметка о времени перевода через объект DB
    time.sleep(0.4)

#sent = SentenceParser()
