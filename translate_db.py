from config import config

#Класс работы с базой
from SingletonDB import SingletonDB
#Класс парсинга фраз перед и после перевода
from SentenceParser import SentenceParser

#Create new object to communicate with database
db1 = SingletonDB()
#Open connection to sqlite3 database file
db1.open(config['db']['sqlite3file'])

#получаем глоссарий из базы в виде словаря
glosary = dict()

#walk on untranslated sentences in DB, sent it to parser
#Получить следующую запись для перевода от объекта DB в цикле пока не кончатся записи
i=2000000000
while True:
    i-=1
    if i<=0:     print('        Exit! ');break
    row = db1.get_next_untranslated_sentence()
    print(vars(db1))
    #id, original_id, from_sent = row[0], row[1], row[2]
    #create parser object
    print(len(row['from']))
    if len(row['from']) > 5000:
        #Если длина исходной строки слишком велика - пропускаем её, отмечаем в базе error=10000
        row['error'] = 10000
        db1.save_translated_sentence(row)
        continue
    print(row)
    sent = SentenceParser(row['from'])

    #Производим перевод, передаём глоссарий в аргументах
    translated_sentence = sent.get_translated(glosary)
    if translated_sentence is None:
        print('THERE IS NO TRANSLATION FROM INTERNET!!!!!!11111oneoneone')
        exit()
    row['to'] = translated_sentence
    #print(sent.__dict__)
    for key in sent.sent_history:
        print ('    ('+str(len(sent.sent_history[key])) + ')    '+key+'    :')
        print (sent.sent_history[key])

    #перевод записывается обратно в базу, делается отметка о времени перевода через объект DB
    if config['translation']['save_translation_to_db']:
        db1.save_translated_sentence(row)
