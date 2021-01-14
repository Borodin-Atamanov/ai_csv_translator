import config
import requests
import json

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

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Api-Key '+config.config['secret_keys']['yandex']['Api-Key'],
        }

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
        #Создаём строку с json-данными для отправки через API-перевода
        translate_json_str = json.dumps(translate_array_to_send, ensure_ascii=True, indent=None, separators=(',', ':') )

        #Получаем перевод от сервиса
        transation_api_result = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate', headers=headers, data=translate_json_str)
        #transation_api_result.content - bytes строка результата
        #transation_api_result.text - обычная строка результата

        #TODO проверять ошибки! Не писать в базу, если есть ошибки перевода! Бросать исключение!

        print ('transation_api_result = ')
        print (type(transation_api_result))
        #print (transation_api_result.__dict__)
        #print ('transation_api_result.text:::')
        #print (transation_api_result.text)
        print ('transation_api_result.content:::')
        #print (transation_api_result.content)

        #Преобразуем полученный ответ из JSON в питонические данные
        pythonic_results = json.loads(transation_api_result.content);
        #print(type(pythonic_results["translations"][0]['text']))
        #print(type(pythonic_results["translations"][0]))
        #print(type(pythonic_results["translations"]))
        #print(type(pythonic_results))
        #print(pythonic_results["translations"][0]['text'])

        self.sent[1] = pythonic_results["translations"][0]['text']
        return self.sent[1]
