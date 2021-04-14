from intervaltree import Interval, IntervalTree
from bs4 import BeautifulSoup
import re
import config
#Класс обращения к службам онлайн-перевода через платный API
from TranslatorOnline import TranslatorOnline
#Класс локального кеширования полученных переводов, чтобы лишний раз не платить
from TranslationCacher import TranslationCacher

#from pprint import pprint
import json
#import copy

class SentenceParser():
    "SentenceParser class used for parse tags and none-tags before and after translation"
    def __init__(self, sent:str):
        """Constructor"""
        #Исходная фраза для перевода
        #Массив разных версий фразы от исходной до результирующией (фраза с самым большим индексом - последняя, результирующая)
        self.sent = list()
        #Исходная фраза
        self.sent.insert(0, sent)   #self.sent[0] = sent

        #Переведённая результирующая фраза
        self.sent.insert(1, None) #self.sent[1] = ''

        #Массив истории перевода
        self.sent_history = {}
        self.sent_history['original'] = self.sent[0]

        #Словарь тегов
        self.tags_start_end = {}
        #Словарь тегов для замены перед переводом
        self.tags_safety_replacement = {}

        #Распарсенная по текст/или тег строка - массив, где ключ=индекс, а по значению - словарь с текстом и его типом (текст/тег)

    def get_translated(self, glosary):
        "Return translated sencence"
        self.glosary = glosary

        #Начинаем обработку строки с простого копирования исходной в результирующую
        self.sent[1] = self.sent[0]

        #половые теги удалены: заменены на первый вариант, фигурные скобки заменены на переводобезопасные символы (может просто удалить всё от символа '|' до символа '}, удалить символ '{')
        self.convert_sex_tags_to_first_comer()

        #Выполняем парсинг фразы на теги и текст
        self.parse()

        #получаем единственную строку, в которой все теги заменены на безопасные для перевода символы
        self.convert_tags_to_safety_chars()

        #Переводим по глоссарию
        self.glossary_translate(glosary)

        #Отправляет строку на перевод через объект перевода, получаем готовый перевод
        self.get_translation_from_internet()

        #превратить переводобезопасные символы обратно в теги
        self.convert_safety_chars_to_tags_back()

        #Возвращаем полученный перевод
        #return 'Perevod na angliysky yazik'
        #return self.sent_history['convert_tags_to_safety_chars']
        return self.sent[1]

    def convert_sex_tags_to_first_comer(self):
        "Method convert all sex-tags (like my 'dear {boy|girl}friend' to 'boyfriend')"
        #Проходимся по строке до тех пор пока не перестанем находить символы "половых" тегов: {,|,}
        #Временная строка-замена sex_tags, которая не должна встретиться в текста
        safety_sex_tag_replacement = '=-z684vg64cawceghn567mi78468nb3v34cx2z3dxzdvz-='
        i=900
        while True:
            pos = {}    #Массив позиций
            pos['start'] = self.sent[1].find(config.config['sex_tags']['start_char'])
            if pos['start'] == -1:
                break
            pos['middle'] = self.sent[1].find(config.config['sex_tags']['middle_char'])
            if pos['middle'] == -1:
                break
            pos['end'] = self.sent[1].find(config.config['sex_tags']['end_char'])
            if pos['end'] == -1:
                break
            pos['max'] = max(pos.values())
            pos['text'] = self.sent[1][pos['start']+1:pos['end']]
            #TODO обрабатываем половой тег (заменяя в тексте на временный вариант?)
            new_string = {}
            new_string[0] = self.sent[1][ 0 : pos['start'] ]
            new_string[1] = self.sent[1][ pos['start']+1 : pos['middle'] ]
            #Добавляем временную строчку вместо окончания полового тега
            new_string[2] = safety_sex_tag_replacement
            new_string[3] = self.sent[1][ pos['end']+1 : len(self.sent[1])+1 ]
            self.sent[1] = '' + new_string[0] + new_string[1] + new_string[2] + new_string[3]
            i-=1
            if i<=0:
                break

        #Создаём строку с пустым половым тегом (обычно "{|}")
        #Вставляем в строку пустой половой тег на то место, где он был примерно, если это указано в конфигурации
        if config.config['sex_tags']['save_empty_sex_tags']:
            empty_sex_tag = config.config['sex_tags']['start_char'] + config.config['sex_tags']['middle_char'] + config.config['sex_tags']['end_char']
        else:
            #Меняем на пустой символ, позиция полового тега в тексте не сохранится
            empty_sex_tag = ''
        self.sent[1] = self.sent[1].replace(safety_sex_tag_replacement, empty_sex_tag)

        self.sent_history['after_sex_tags_crop'] = self.sent[1]
        return True

    def parse(self):
        "Parse sentence into subsentences"

        if config.config['translation']['change_html_entities_to_utf8_chars']:
            self.soup = BeautifulSoup(self.sent[1], "html.parser")
            self.sent[1] = self.soup.prettify(formatter="minimal")
            self.sent[1] = str(self.soup)
        self.sent[1] = self.sent[1] #Don't change HTML-entities to UTF8-chars

        #self.show_tags()

        #Определяем разные теги в цикле
        for regex in config.config['regex_tags']:
            #print (regex)
            self.find_start_end_of_the_tag(regex)

        #слить соседние теги воедино: если окончание тега рядом с началом следующего - то записать единое начало-конец
        self.join_tags_starts_ends()

        #self.show_tags()
        return True

    def convert_tags_to_safety_chars(self):
        "Method change all tags in self.sent[1] to safety-for-translation chars, save table of this translation in self.tags_safety_replacement"
        #Результат работы метода - массив соответствия исходных тегов и безопасных для онлайн-перевода self.tags_safety_replacement и изменённая строка данных (где исходные теги заменены на безопасные для перевода временные последовательности)
        print ("\n\n")
        self.tags_safety_replacement = {}

        #Символ, безопасный для перевода
        si=config.config['translation']['safety_for_translation_sign']
        #Минимальное Количество символов, безопасных для перевода и замены в тегах
        cs=config.config['translation']['minimum_safety_for_translation_chars']
        #Добавлять этот символ вокруг переводобезопасных символов
        ad=config.config['translation']['add_this_char_around_safety_for_translation_sign']


        #Какой вариант преобразования тегов во временные символы используется?
        if config.config['translation']['use_only_one_safety_char_for_each_tag']:
            #Один тегобезопасный символ повторяется несколько раз (разное количество решёток заменяет разные теги)
            #Проходимся по тегам, от конца в начало, генерируем безопасные-для перевода замены
            i=0
            for key in tuple(sorted(self.tags_start_end, reverse=True)):
                i+=1
                code = ''+si*(i+cs)+'' #repeat si string i+cs times
                self.tags_safety_replacement[code] = self.tags_start_end[key]['text']
        else:
            #Используется только один тегобезопасный символ для любого тега (каждый тег заменяется одной решёточкой)
            #Проходимся от начала к концу, помечаем запоминаем какой тег на какой теговой позиции в строке
            i=0
            for key in tuple(sorted(self.tags_start_end, reverse=False)):
                i+=1
                code = config.config['translation']['tempory_tag_template'].format(i);
                #print(code, self.tags_start_end[key])
                self.tags_safety_replacement[code] = self.tags_start_end[key]['text']

        print (self.tags_safety_replacement)

        #Какой вариант преобразования тегов во временные символы используется?
        if config.config['translation']['use_only_one_safety_char_for_each_tag']:
            #Один тегобезопасный символ повторяется несколько раз (разное количество решёток заменяет разные теги)
            #Проходимся по тегам, от конца в начало, генерируем безопасные-для перевода замены
            #Отсортируем массив по длинам строк тегов, начиная с самых длинных, чтобы сначала заменять более длинные теги сначала, ведь более короткие теги могут повторяться внутри более длинных!
            self.tags_safety_replacement = {k: v for k,v in sorted(self.tags_safety_replacement.items(), reverse=True, key=lambda item: len(str(item[1]))) }
            print('Отсортировано по длине тегов: ', self.tags_safety_replacement)
            #Превратим теги в переводобезопасные символы, начиная с самых длинных тегов
            for key in tuple(self.tags_safety_replacement):
                self.sent[1] = self.sent[1].replace(self.tags_safety_replacement[key], ad+key+ad, 1)
        else:
            #Используется только один тегобезопасный символ для любого тега (каждый тег заменяется одной решёточкой)
            for key in tuple(self.tags_safety_replacement):
                self.sent[1] = self.sent[1].replace(self.tags_safety_replacement[key], ad+si+ad, 1)

        print (json.dumps(self.tags_safety_replacement, ensure_ascii=False, indent=4, separators=(',', ':') ) )
        #print ("Input\n", self.sent[0], "\nResult\n", self.sent[1], "\n")

        self.sent_history['convert_tags_to_safety_chars'] = self.sent[1] #save to history

        #self.show_tags()
        return True

    def convert_safety_chars_to_tags_back(self):
        "Method replace all safety-to-translate tags to original tags, using self.tags_safety_replacement"
        #Отсортируем массив по длинам строк тегов, начиная с самых длинных, чтобы сначала заменять более длинные теги, ведь длина имеет значение при строковых операциях!

        #Символ, безопасный для перевода
        si=config.config['translation']['safety_for_translation_sign']
        #Добавлять этот символ вокруг переводобезопасных символов
        ad=config.config['translation']['add_this_char_around_safety_for_translation_sign']

        #Убираем добавленные символы (вокруг тегозамещающих решёток). То есть до решётки и после решётки убирается пробел
        if config.config['translation']['add_this_char_around_safety_for_translation_sign']:
            for i in range(0, 17):
                self.sent[1] = self.sent[1].replace(si+ad, si)
                self.sent[1] = self.sent[1].replace(ad+si, si)

        #Убираем дублирующиеся символы, которые добавляются вокруг обезопашивающих теги символов. (Обычно два пробела заменяем на один)
        if config.config['translation']['remove_dublicate_char_around_safety_for_translation_sign']:
            for i in range(0, 17):
                self.sent[1] = self.sent[1].replace(ad+ad, ad)

        #Какой вариант преобразования тегов во временные символы используется?
        if config.config['translation']['use_only_one_safety_char_for_each_tag']:
            #Один тегобезопасный символ повторяется несколько раз (разное количество решёток заменяет разные теги)
            #Превратим переводобезопасные коды в исходные теги, начиная с самых длинных кодов
            sorted_by_key_len_tuple = tuple( sorted(self.tags_safety_replacement, key=len, reverse=True))
            #print('Отсортировано по убыванию длины тегов: ', sorted_by_key_len_tuple)
            for key in sorted_by_key_len_tuple:
                self.sent[1] = self.sent[1].replace(key, self.tags_safety_replacement[key], 1)
        else:
            #Используется только один тегобезопасный символ для любого тега (каждый тег заменяется одной решёточкой)
            #Сначала превратим каждую встреченную решёточку в подстроку вида <!-- TAG_ID=4 -->
            for key in self.tags_safety_replacement:
                #Находим первую решётку, заменяем её на <!-- TAG_ID=1 -->, продолжаем
                self.sent[1] = self.sent[1].replace(si, key, 1)
            #Пройдёмся по тегам, превратить строки вида <!--TAG_ID=4--> в исходные теги
            for key in self.tags_safety_replacement:
                self.sent[1] = self.sent[1].replace(key, self.tags_safety_replacement[key], 1)

        self.sent_history['convert_safety_chars_to_tags_back'] = self.sent[1] #save to history
        self.show_tags()
        return True

    def find_start_end_of_the_tag(self, regex:str):
        "Method return dict with start and end positions of found tags"
        regul = re.compile(regex, re.DOTALL)
        for reg_obj in regul.finditer(self.sent[1]):
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
            self.tags_start_end[key]['text'] = self.sent[1][self.tags_start_end[key]['start']:self.tags_start_end[key]['end']]

        #отсортировать все теги по позиции начала
        self.tags_start_end = {k: v for k,v in sorted(self.tags_start_end.items(), reverse=False, key=lambda item: item[1].get('start', 0)) }
        return True

    def join_tags_starts_ends(self):
        "Method joins start and end position of tags together if they stays together (end of one tag is start of another)"

        #отсортировать все теги по позиции начала
        self.sort_tags_starts_ends()

        #Новое интервальное дерево создаём
        tree = IntervalTree()
        #Проходимся по тегам, преобразуем в интервальное дерево
        #Используем хитрость: от позиции старта отнимаем сотую к позиции конца прибавляем сотую, чтобы интервалы накладывались с перехлёстом, и легко определялись методом merge_overlaps() Такой вот трюк
        for key in tuple(self.tags_start_end):
            tree.addi(self.tags_start_end[key]['start']-0.01, self.tags_start_end[key]['end']+0.01)

        for interval_obj in sorted(tree):
            #print (interval_obj.begin, ' -- ', interval_obj.end)
            pass
        #Объединяем пересекающиеся интервалы
        tree.merge_overlaps()
        for interval_obj in sorted(tree):
            #print (interval_obj.begin, ' -- ', interval_obj.end)
            pass

        #Преобразуем дерево обратно в словарь тегов (в формат, понятный этому объекту)
        new_tags = {}
        for interval_obj in sorted(tree):
            #print (interval_obj.begin, '--', interval_obj.end)
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
        print("\nself.tags_start_end:")
        for key in self.tags_start_end:
            #show_str = show_str.join("\n").join(str(key)).join(": ").join(str(self.tags_start_end[key]))
            print(key, self.tags_start_end[key])

        print("\ntags_safety_replacement")
        for key in self.tags_safety_replacement:
            print("[", key,  "] [",self.tags_safety_replacement[key], "]", sep="")
            pass

        #print (show_str)
        #print (self.__dict__)
        #return show_str

    def glossary_translate(self, glosary:dict):
        "find and replace by glossary"
        return True

    def get_translation_from_internet(self):
        "Method translate text, using object of TranslatorOnlineclass"
        #self.sent_history['before_translate'] = self.sent[1]
        #Создаём объект онлайн-перевода
        self.TranslatorOnline = TranslatorOnline(self.sent[1])
        self.sent[1] = self.TranslatorOnline.get_translated()
        self.sent_history['after_translate'] = self.sent[1]

        #Убираем мусорные пробельные символы находящиеся между "переводобезопасными символами"
        s='\\'+config.config['translation']['safety_for_translation_sign']
        #Формируем строку поиска по шаблону "#(пробелы)#"
        finder_str = ''+s+r'[\s\r\n]{1,}'+s+''
        for i in range(0, 17):
            #r'\#[\s\r\n]{1,}\#' --> '##'
            self.sent[1] = re.sub(finder_str, config.config['translation']['safety_for_translation_sign']*2, self.sent[1])

        #print (f'Результат перевода: {self.sent[1]}');
        self.sent_history['cleaning_after_translate'] = self.sent[1]
        return True


