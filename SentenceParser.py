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
        #Массив разных версий фразы от исходной до результирующией (фраза с самым большим индексом - последняя, результирующая)
        self.sent = {}
        #Исходная фраза
        self.sent['00-input'] = sent
        self.sent['10-soup'] = ''
        #Переведённая фраза
        self.sent['99-ready'] = ''
        #Словарь тегов
        self.tags_start_end = {}
        #Словарь тегов для замены перед переводом
        self.tags_safety_replacement = {}

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
        return self.sent['99-ready']

    def parse(self):
        "Parse sentence into subsentences"
        self.soup = BeautifulSoup(self.sent['input'], "html.parser")
        self.sent['10-soup'] = self.soup.prettify(formatter="minimal")
        self.sent['10-soup'] = str(self.soup)
        self.sent['10-soup'] = self.sent #Don't change HTML-entities to UTF8-chars

        self.show_tags()

        #HTML-сущности цифровые
        regex = r'\s*&#\d{,7};\s*';
        self.find_start_end_of_the_tag(regex)

        #HTML-сущности буквенные
        regex = r'\s*&[#0-9a-zA-Z]{,7};\s*';
        self.find_start_end_of_the_tag(regex)

        #Все %%-теги от % до % и пробельные символы до и после тега
        #Между %% не может быть киррилица!
        #TODO проверить работу этой регулярки! (Сейчас поведение не предсказуемо!)
        #Исправить регулярку так, чтобы она не включала русские буквы между символами %%
        #Длина строки между %% ограничена
        regex = r'\s*%[^А-я]{,17}%\s*';
        self.find_start_end_of_the_tag(regex)

        #Все HTML-теги: от < до > и пробельные символы до и после тега
        regex = r'\s*<.*?>\s*';
        self.find_start_end_of_the_tag(regex)

        #слить соседние теги воедино: если окончание тега рядом с началом следующего - то записать единое начало-конец
        self.join_tags_starts_ends()

        self.show_tags()

        return True

    def convert_tags_to_safety_chars(self):
        "Method change all tags in self.output to safety-for-translation chars, save table of this translation"
        #Проходимся по тегам, от конца в начало, преобразуем генерируем безопасные-для перевода замены
        #Результат работы метода - массив соответствия исходных тегов и безопасных для онлайн-перевода и изменённая строка данных
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
            self.tags_start_end[key]['text'] = self.sent['10-soup'][self.tags_start_end[key]['start']:self.tags_start_end[key]['end']]

        #отсортировать все теги по позиции начала
        self.tags_start_end = {k: v for k,v in sorted(self.tags_start_end.items(), reverse=False, key=lambda item: item[1].get('start', 0)) }
        return True

    def join_tags_starts_ends(self):
        "Method joins start and end position of tags together if they stays together (end of one tag is start of another)"

        print("join_tags_starts_ends()")

        #отсортировать все теги по позиции начала
        self.sort_tags_starts_ends()

        #Новое интервальное дерево создаём
        tree = IntervalTree()
        #Проходимся по тегам, преобразуем в интервальное дерево
        #Используем хитрость: от позиции старта отнимаем сотую к позиции конца прибавляем сотую, чтобы интервалы накладывались с перехлёстом, и легко определялись методом merge_overlaps() Такой вот трюк
        for key in tuple(self.tags_start_end):
            tree.addi(self.tags_start_end[key]['start']-0.01, self.tags_start_end[key]['end']+0.01)

        for interval_obj in sorted(tree):
            print (interval_obj.begin, ' -- ', interval_obj.end)
        #Объединяем пересекающиеся интервалы
        print ('join!!')
        tree.merge_overlaps()
        for interval_obj in sorted(tree):
            print (interval_obj.begin, ' -- ', interval_obj.end)

        #Преобразуем дерево обратно в словарь тегов (в формат, понятный этому объекту)
        new_tags = {}
        for interval_obj in sorted(tree):
            print (interval_obj.begin, '--', interval_obj.end)
            key = len(new_tags)+1
            new_tags[key] = {'start':int(round(interval_obj.begin)), 'end':int(round(interval_obj.end))}
        self.tags_start_end = new_tags

        #отсортировать все теги по позиции начала
        self.sort_tags_starts_ends()

        #self.show_tags()
        #Объединяем теги, которые стоят рядом или накладываются друг на друга
        #Вложенные циклы проверки наложения или соседства тегов


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

