from config import config

#Класс работы с базой
from SingletonDB import SingletonDB
#Класс парсинга фраз перед и после перевода
from SentenceParser import SentenceParser

#Create new object to communicate with database
db1 = SingletonDB()
#Open connection to sqlite3 database file
db1.open(config['db']['sqlite3file'])

print("Enter/Paste your text to translate. Press Ctrl-D or Ctrl-Z (Шindows) to save it.")
input_content = []
while True:
    try:
        line = input()
    except EOFError:
        break
    #print (line)
    input_content.append(line)
input_text = "\n".join(input_content)

#create parser object
sent = SentenceParser(input_text)

#Производим перевод, передаём глоссарий в аргументах
translated_sentence = sent.get_translated({})
if translated_sentence is None:
    print('ERROR! THERE IS NO TRANSLATION FROM INTERNET!!!!!!11111oneoneone')
    exit()

output_text = translated_sentence

for key in sent.sent_history:
    print ('    ('+str(len(sent.sent_history[key])) + ')    '+key+'    :')
    print (sent.sent_history[key])

print ("\n\n\nResult:\n\n" + output_text)
