from config import config

#Класс работы с базой
from SingletonDB import SingletonDB
#Класс парсинга фраз перед и после перевода
from SentenceParser import SentenceParser

#Create new object to communicate with database
db1 = SingletonDB()
#Open connection to sqlite3 database file
db1.open(config['db']['sqlite3file'])

#TODO получаем глоссарий из базы в виде словаря
glosary = dict()

#test_text = """<p>Этот доспех собирался лучшими инженерами подгорного племени.&nbsp;</p>\n<p><font color="#FF0000"><b> Для использования требует 450&nbsp;Доблести. </b></font></p>\n<p><font color="#0000ff">Общее количество надетых предметов ограничено значением вашей Доблести.</font></p>\n %SPECIAL_TAG%   """
test_text = """<p tag=1> Далее tag2  &nbsp;</p tag=2>\n<p><font color="#FF0000"><b> А ещё далее TAG3 </b tag=3></font></p>\n<p><font color="#0000ff">TAG4</font tag=4></p>\n %SPECIAL_TAG  tag=5%TAG5<p tag=6>tag6<p tag=7> Ля-л Flower-light_3-4_red
(% VERY SPECIAL_TAG %)
  Как тебе такое?
{Хар-ка id=1022}, {Хар-ка id=1022#bool}

"""
sent = SentenceParser(test_text)
translated_sentence = sent.get_translated(glosary)
for key in sent.sent_history:
    print (f'   {key}:')
    print (sent.sent_history[key])
exit()

#walk on untranslated sentences in DB, sent it to parser
#Получить следующую запись для перевода от объекта DB в цикле пока не кончатся записи
i=0
while True:
    row = db1.get_next_untranslated_sentence()
    #print(repr(row))
    #print(vars(db1))
    #id, original_id, from_sent = row[0], row[1], row[2]
    #create parser object
    sent = SentenceParser(row['from'])
    #Производим перевод, передаём глоссарий в аргументах
    translated_sentence = sent.get_translated(glosary)
    row['to'] = translated_sentence
    #print(sent.__dict__)
    for key in sent.sent_history:
        print (f'   {key}:')
        print (sent.sent_history[key])

    print ()
    #перевод записывается обратно в базу, делается отметка о времени перевода через объект DB
    db1.save_translated_sentence(row)
    i+=1
    if i>10:     break

#sent = SentenceParser()
