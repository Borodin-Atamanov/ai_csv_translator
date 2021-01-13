from config import *
import random

#Create new object to communicate with database
db1 = SingletonDB()
#Open connection to sqlite3 database file
db1.open(config['db']['sqlite3file'])

#TODO получаем глоссарий из базы в виде словаря
glosary = dict()

#test_text = """<p>Этот доспех собирался лучшими инженерами подгорного племени.&nbsp;</p>\n<p><font color="#FF0000"><b> Для использования требует 450&nbsp;Доблести. </b></font></p>\n<p><font color="#0000ff">Общее количество надетых предметов ограничено значением вашей Доблести.</font></p>\n %SPECIAL_TAG%   """
#test_text = """<p> Далее tag2  &nbsp;</p>\n<p><font color="#FF0000"><b> А ещё далее TAG3 </b></font></p>\n<p><font color="#0000ff">TAG4</font></p>\n %SPECIAL_TAG%TAG5<p>tag6<p>   """
#sent = SentenceParser(test_text)
#translated_sentence = sent.get_translated(glosary)

#walk on untranslated sentences in DB, sent it to parser
#Получить следующую запись для перевода от объекта DB в цикле пока не кончатся записи
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
    #TODO перевод записывается обратно в базу, делается отметка о времени перевода через объект DB
    db1.save_translated_sentence(row)
    time.sleep(0.4)

    rnd = random.gauss(10, 1)
    #print(rnd)
    if rnd >= 11:
        break

#sent = SentenceParser()
