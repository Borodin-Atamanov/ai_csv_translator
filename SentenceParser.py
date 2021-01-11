from bs4 import BeautifulSoup
import re
#from pprint import pprint
#import json
import functools

class SentenceParser():
    "SentenceParser class used for parse tags and none-tags before and after translation"
    def __init__(self, sent:str):
        """Constructor"""
        self.sent = sent
        self.output = None
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

        #Все HTML-теги: от < до > и пробельные символы до и после тега
        regex = r'\s*<.*?>\s*';
        self.find_start_end_of_the_tag(regex)

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
        #print(repr(self.tags_start_end))
        return True

    def find_start_end_of_the_tag(self, regex:str):
        "Method return dict with start and end positions of found tags"
        regul = re.compile(regex, re.DOTALL)
        for reg_obj in regul.finditer(self.output):
            #dict to save start and end positions of tag
            tags_start_end_local = {}
            tags_start_end_local['start'] = reg_obj.start()
            tags_start_end_local['end'] = reg_obj.end()
            tags_start_end_local['group'] = reg_obj.group()
            key = str(str(tags_start_end_local['start']) + '-' + str(tags_start_end_local['end']) + '-' + reg_obj.group())
            self.tags_start_end[key] = tags_start_end_local;
        self.sort_tags_starts_ends()    #sort tags dict
        return True

    def sort_tags_starts_ends(self):
        "Method sort tags_start_end by start position"
        #отсортировать все теги по позиции начала
        tags_keys_in_sorted_order = sorted(self.tags_start_end, key=lambda x: int(self.tags_start_end[x]['start']), reverse=False) #Сортирует, но возвращает только list ключей, не dict значений
        new_tags_start_end = {}
        #Проходимся в цикле по списку tags_keys_in_correct_order, создаём новый словарь данных, куда записываем данные из словаря self.tags_start_end но в порядке ключей из tags_keys_in_sorted_order
        for ikey in tags_keys_in_sorted_order:
            #print(ikey)
            new_tags_start_end[ikey] = self.tags_start_end[ikey]
        #Установим отсортированный список тегов в свойства объекта
        self.tags_start_end = new_tags_start_end
        return self.tags_start_end

    def join_tags_starts_ends(self):
        "Method joins start and end position of tags together if they stays together (end of one tag is start of another)"
        #отсортировать все теги по позиции начала
        self.sort_tags_starts_ends()
        new_tags_start_end = {}
        #Проходимся по всем тегам, находим стоящие рядом, объединяем в новый словарь
        #Стоящие рядом теги - это такие у которых start предыдущего равен end позиции следующего
        for key in self.tags_start_end:
            print (self.tags_start_end.get(key, 0)['start'], self.tags_start_end.get(prev_key, 0)['end'])
            prev_key = key
            print (self.tags_start_end[key])

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

