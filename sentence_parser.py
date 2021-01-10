class SentenceParser():
    "SentenceParser class used for parse tags and none-tags before and after translation"
    def __init__(self, sent:str):
        """Constructor"""
        self.sent = sent;

    def get_translated(self, glosary):
        "Return translated sencence"
        self.glosary = glosary
        #Выполняем парсинг фразы
        self.parse()
        #Переводим по глоссарию
        self.glossary_translate(glosary)
        #TODO получаем единственную фразу, в которой все теги заменены на безопасные для перевода символы
        #TODO2 половые теги удалены: заменены на первый вариант, фигурные скобки заменены на переводобезопасные символы (может просто удалить всё от символа '|' до символа '}, удалить символ '{')
        #TODO Пробуем получить перевод из кеша переводов
        #Если в кеше точный перевод не нашёлся:
        #TODO создаём объект онлайн-перевода
        #TODO Отправляет строку на перевод через объект перевода, получаем готовый перевод
        #TODO Записывается результат перевода в локальный кэш
        #TODO превратить переводобезопасные символы обратно в теги
        #Возвращаем полученный перевод
        return 'Perevod na angliysky yazik'

    def parse(self):
        "Parse sentence into subsentences"
        return True

    def glossary_translate(self, glosary:dict):
        "find and replace by glossary"
        return True
    

