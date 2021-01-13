import config

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
        symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
                u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")

        tr = {ord(a):ord(b) for a, b in zip(*symbols)}
        self.sent[1] = self.sent[0].translate(tr)
        return self.sent[1]
