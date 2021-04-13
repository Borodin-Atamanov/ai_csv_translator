import config
import requests
import json
#Класс работы с базой
from SingletonDB import SingletonDB


class TranslatorOnline():
    def __init__(self, sent:str):
        """Constructor"""
        #Массив разных версий фразы от исходной[0] до результирующией[1]
        self.sent = list()
        #Исходная фраза
        self.sent.insert(0, sent)   #self.sent[0] = sent
        #Переведённая результирующая фраза
        self.sent.insert(1, '') #self.sent[1] = ''

        #Массив истории перевода
        self.sent_history = {}
        pass

    def get_translated(self):
        "Return translated sentence"

        #TODO Пробуем получить перевод из кеша переводов
        #self.get_translation_from_cache()
        #Create new object to communicate with database
        db1 = SingletonDB()
        #Open connection to sqlite3 database file
        db1.open(config.config['db']['sqlite3file'])
        cache_row = db1.get_from_cache({'from': self.sent[0]})
        #print(vars(db1))
        #If sentence is empty string - than translation is empty string too
        if self.sent[0] == '':
            print (f"       Пустая строка")
            self.sent[1] = ''
            #Вернём перевод из кеша
            return self.sent[1]

        #id, original_id, from_sent = row[0], row[1], row[2]
        if cache_row is not None and cache_row.get('to') is not None:
            #В кеше нашёлся точный перевод,
            print (f"       Перевод нашёлся в кеше! {cache_row['to']}")
            print (f"{self.sent}")
            self.sent[1] = cache_row['to']
            #Вернём перевод из кеша
            return self.sent[1]
        else:
            #Если в кеше точный перевод не нашёлся:
            #создаём объект онлайн-перевода
            #HTTP-Заголовок запроса
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Api-Key '+config.config['secret_keys']['yandex']['Api-Key'],
            }

            #Массив отправляемых на перевод данных
            translate_array_to_send = \
            {
                #folderId нужен для авторизации при переводе?
                "folderId": config.config['secret_keys']['yandex']['folderId'],
                #Массив текстов, отправляемых на перевод, можно отправлять несколько в одном запросе
                "texts": [self.sent[0]],
                "sourceLanguageCode": config.config['translation']['sourceLanguageCode'],
                "targetLanguageCode": config.config['translation']['targetLanguageCode'],
                "format": config.config['translation']['format'],
            }
            print (translate_array_to_send);
            #Создаём строку с json-данными для отправки через API-перевода
            translate_json_str = json.dumps(translate_array_to_send, ensure_ascii=True, indent=None, separators=(',', ':') )

            #Получаем перевод от сервиса
            transation_api_result = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate', headers=headers, data=translate_json_str)
            #transation_api_result.content - bytes строка результата
            #transation_api_result.text - обычная строка результата

            #Преобразуем полученный ответ из JSON в питонические данные
            pythonic_results = json.loads(transation_api_result.content)
            #проверять ошибки! Не писать в базу, если есть ошибки перевода! Бросать исключение!
            try:
                self.sent[1] = pythonic_results["translations"][0]['text']
            except KeyError:
                print (transation_api_result.__dict__)
                #print(type(pythonic_results))
                #print(type(pythonic_results["translations"]))
                #print(type(pythonic_results["translations"][0]))
                #print(type(pythonic_results["translations"][0]['text']))
                #print(pythonic_results["translations"][0]['text'])
                exit()
                return None
            #Строка данных перевода

            #записать перевод в кеш переводов в базу данных
            db1.save_to_cache({'from':self.sent[0], 'to':self.sent[1]})
            print(db1)

            return self.sent[1]
