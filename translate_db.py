from config import *

#Create new object to communicate with database
db1 = SingletonDB()
#Open connection to sqlite3 database file
db1.open(db['sqlite3file'])

#TODO получаем глоссарий из базы в виде словаря
glosary = dict()

#walk on untranslated sentences in DB, sent it to parser
#Получить следующую запись для перевода от объекта DB в цикле пока не кончатся записи
row = db1.get_next_untranslated_sentence()
print(row)
print(vars(db1))
#print(vars(row))
#print(repr(row))

id, original_id, from_sent = row[0], row[1], row[2]
#create parser object
sent = SentenceParser(from_sent)

#print(vars(sent))
#Производим перевод, передаём глоссарий в аргументах
#translated_sentence = sent.get_translated(glosary)
#TODO перевод записывается обратно в базу, делается отметка о времени перевода через объект DB
time.sleep(0.4)

#sent = SentenceParser()
