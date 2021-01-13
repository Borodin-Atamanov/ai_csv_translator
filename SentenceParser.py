from intervaltree import Interval, IntervalTree
from bs4 import BeautifulSoup
import re
#from pprint import pprint
#import json
#import copy

class SentenceParser():
    "SentenceParser class used for parse tags and none-tags before and after translation"
    def __init__(self, sent:str):
        """Constructor"""
        #Исходная фраза для перевода
        self.sent = sent
        #Переведённая фраза
        self.output = ''
        #Словарь тегов
        self.tags_start_end = {}

    def get_translated(self, glosary):
        "Return translated sencence"
        self.glosary = glosary

        #Выполняем парсинг фразы
        self.parse()

        #TODO2 половые теги удалены: заменены на первый вариант, фигурные скобки заменены на переводобезопасные символы (может просто удалить всё от символа '|' до символа '}, удалить символ '{')
        self.convert_sex_tags_to_first_comer()

        #TODO получаем единственную фразу, в которой все теги заменены на безопасные для перевода символы
        self.convert_tags_to_safety_chars()

        #Переводим по глоссарию
        self.glossary_translate(glosary)

        #TODO Пробуем получить перевод из кеша переводов
        self.get_translation_from_cache()

        #Если в кеше точный перевод не нашёлся:
        #TODO создаём объект онлайн-перевода
        self.get_translation_from_internet()
        #TODO Отправляет строку на перевод через объект перевода, получаем готовый перевод

        #TODO Записывается результат перевода в локальный кэш
        self.save_translation_to_cache()

        #TODO превратить переводобезопасные символы обратно в теги
        self.convert_safety_chars_to_tags_back()

        #Возвращаем полученный перевод
        #return 'Perevod na angliysky yazik'
        return self.output

    def parse(self):
        "Parse sentence into subsentences"
        self.soup = BeautifulSoup(self.sent, "html.parser")
        self.output = self.soup.prettify(formatter="minimal")
        self.output = str(self.soup)
        self.output = self.sent #Don't change HTML-entities to UTF8-chars

        self.show_tags()

        #Все HTML-теги: от < до > и пробельные символы до и после тега
        regex = r'\s*<.*?>\s*';
        self.find_start_end_of_the_tag(regex)
        self.show_tags()

        #Все %%-теги от % до % и пробельные символы до и после тега
        #Между %% не может быть киррилица!
        #TODO проверить работу этой регулярки! (Сейчас поведение не предсказуемо!)
        #Исправить регулярку так, чтобы она не включала русские буквы между символами %%
        #Длина строки между %% ограничена
        regex = r'\s*%[^А-я]{,17}%\s*';
        self.find_start_end_of_the_tag(regex)

        #HTML-сущности цифровые
        regex = r'\s*&#\d{,7};\s*';
        self.find_start_end_of_the_tag(regex)

        #HTML-сущности буквенные
        regex = r'\s*&[#0-9a-zA-Z]{,7};\s*';
        self.find_start_end_of_the_tag(regex)

        #слить соседние теги воедино: если окончание тега рядом с началом следующего - то записать единое начало-конец
        self.join_tags_starts_ends()
        return True

    def find_start_end_of_the_tag(self, regex:str):
        "Method return dict with start and end positions of found tags"
        regul = re.compile(regex, re.DOTALL)
        for reg_obj in regul.finditer(self.output):
            #dict to save start and end positions of tag
            key = len(self.tags_start_end)
            self.tags_start_end[key] = {}
            self.tags_start_end[key]['start'] = reg_obj.start()
            self.tags_start_end[key]['end'] = reg_obj.end()
            #self.tags_start_end[key]['text'] = reg_obj.group()

        self.sort_tags_starts_ends()    #sort tags dict
        return True

    def sort_tags_starts_ends(self):
        "Method sort tags_start_end by start position"

        for key in tuple(self.tags_start_end):
            #Добавим информацию о теге, посчитаем длину, текст тега, etc
            self.tags_start_end[key]['len'] = self.tags_start_end[key]['end'] - self.tags_start_end[key]['start']
            self.tags_start_end[key].setdefault('join', 'j' + str(self.tags_start_end[key]['start']) + '--' + str(self.tags_start_end[key]['end']));
            self.tags_start_end[key]['text'] = self.output[self.tags_start_end[key]['start']:self.tags_start_end[key]['end']]

        #отсортировать все теги по позиции начала
        self.tags_start_end = {k: v for k,v in sorted(self.tags_start_end.items(), reverse=False, key=lambda item: item[1].get('start', 0)) }
        return True

    def join_tags_starts_ends(self):
        "Method joins start and end position of tags together if they stays together (end of one tag is start of another)"
        #отсортировать все теги по позиции начала
        new_tags_start_end = {} #Новый словарь для объединённых тегов

        print("join_tags_starts_ends()")
        self.sort_tags_starts_ends()

        self.show_tags()
        #Объединяем теги, которые стоят рядом или накладываются друг на друга
        #Вложенные циклы проверки наложения или соседства тегов
        delete_this_keys = set()
        new_tags = {}
        #new_tags = (self.tags_start_end) #Словарь для объединённых и прежних
        i=0
        for keya in tuple(self.tags_start_end):
            for keyb in tuple(self.tags_start_end):
                #Проверяем, являются ли последние два тега пересекающимися, соседними
                #Теги объединяются, если начало или конец одного тега лежит внутри другого тега
                i+=1
                mina = min(
                self.tags_start_end[keya]['start'],
                self.tags_start_end[keya]['end'])
                maxa = max(
                self.tags_start_end[keya]['start'],
                self.tags_start_end[keya]['end'])
                minb = min(
                self.tags_start_end[keyb]['start'],
                self.tags_start_end[keyb]['end'])
                maxb = max(
                self.tags_start_end[keyb]['start'],
                self.tags_start_end[keyb]['end'])

                if (mina <= minb <= maxa) or (mina <= maxb <= maxa):
                    #теги соседние и(ли) пересекаются, объединим их в один тег
                    new_joined_tag = {}
                    new_joined_tag['start'] = min(mina, minb)
                    new_joined_tag['end'] = max(maxa, maxb)
                    new_key = str(new_joined_tag['start']) + '--' + str(new_joined_tag['end'])
                    new_key = len(new_tags)+1
                    new_tags[new_key] = new_joined_tag
                    #print ("Соединяем тег в ", new_joined_tag);

                    #Удалим исходные теги, (останется только новый объединённый тег)
                    delete_this_keys.add(keya)
                    delete_this_keys.add(keyb)
                    pass
                else:
                    #Теги не соседние
                    new_key = len(new_tags)+1
                    new_tags[new_key] = self.tags_start_end[keyb]
                    pass


        print ("Iterations", i)
        self.tags_start_end = new_tags
        self.sort_tags_starts_ends()
        self.show_tags()

        print("Удаляем объединённые теги: ")
        delete_this_keys = (set(delete_this_keys))
        print (delete_this_keys)
        for key in delete_this_keys:
            #print ('Удаляем ', key, type(key))
            if key in self.tags_start_end:
                del self.tags_start_end[key]

        print("После удаления:")
        self.sort_tags_starts_ends()
        self.show_tags()

        return True

    def show_tags(self):
        "Method show found tags"
        show_str = ''
        for key in self.tags_start_end:
            #show_str = show_str.join("\n").join(str(key)).join(": ").join(str(self.tags_start_end[key]))
            print(key, self.tags_start_end[key])
        #print (show_str)
        #return show_str


    def glossary_translate(self, glosary:dict):
        "find and replace by glossary"
        return True

    def convert_sex_tags_to_first_comer(self):
        "Method"
        return True

    def convert_tags_to_safety_chars(self):
        "Method"
        return True

    def get_translation_from_cache(self):
        "Method"
        return True

    def get_translation_from_internet(self):
        "Method"
        return True

    def convert_safety_chars_to_tags_back(self):
        "Method"
        return True

    def save_translation_to_cache(self):
        "Method"
        return True

