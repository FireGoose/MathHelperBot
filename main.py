import os
import sqlite3
import telebot
import typing as tp

from telebot import types

bot = telebot.TeleBot('6264076732:AAHcQ724Ah5dmTYz2WoTbzmrnTvSM9FK7NA')
user_id = 'base'


@bot.message_handler(commands=['start'])
def start(message):
    global user_id, data
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Поздороваться")
    markup.add(btn1)
    bot.send_message(message.from_user.id,
                     "Привет! Я твой бот-помощник для запоминания различных математических законов.",
                     reply_markup=markup)
    user_id = str(message.from_user.id)
    print(user_id)
    data = Data()


def sqlite_lower(string):
    """Переопределение функции преобразования к нижнему регистру"""

    return string.lower()


def sqlite_upper(string):
    """Переопределение функции преобразования к верхнему регистру"""

    return string.upper()


class DataEntity:
    """Класс строки базы данных"""

    def __init__(self, entity: tuple) -> None:
        self.entity = entity
        if entity:
            self.id = entity[0]
            self.name = entity[1]
            self.formula = entity[2]
            self.section = entity[3]


class Data:
    """Класс для работы с базой данных sqlite"""

    def __init__(self) -> None:
        if not os.path.exists('./data'):  # Создание папки с базой данных
            os.mkdir('./data')

        query = """CREATE TABLE IF NOT EXISTS "maths" (
                'id' INTEGER PRIMARY KEY AUTOINCREMENT,
                'name' TEXT UNIQUE,
                'formula' TEXT,
                'section' TEXT
                )"""
        self.execute_query(query)  # Создание базы данных
        self.cursor: tp.Optional[sqlite3.Cursor] = None
        self.name_error: bool = False

    def execute_query(self, query: str, fields=tuple()) -> DataEntity:
        """Исполнение запроса в базу данных"""

        with sqlite3.connect('./data/' + user_id + '.db') as db:
            db.create_function("LOWER", 1, sqlite_lower)
            db.create_function("UPPER", 1, sqlite_upper)
            self.cursor = db.cursor()
            result = self.cursor.execute(query, fields).fetchall()
            db.commit()
            if result:
                entity = DataEntity(result[0])
                return entity
            entity = DataEntity(tuple())
            return entity

    def show_error_window(self):
        """Функция показа виджета ошибки отсутствующей строки"""

        pass

    def add(self, name: str, formula: str, section: str) -> None:
        """Добавление строки в базу данных"""

        query = f"""INSERT INTO maths(name, formula, section) VALUES(?, ?, ?)"""
        self.execute_query(query, (name, formula, section))

    def update_formula(self, name: str, formula: str) -> None:
        """Изменение формулы в строке базы данных"""

        if not self.select_values(name).entity:
            return

        query = f"""UPDATE maths 
                SET formula = ? 
                WHERE LOWER(name) = ?"""
        self.execute_query(query, (formula, name.lower()))

    def update_section(self, name: str, section: str) -> None:
        """Изменение раздела математики в строке базы данных"""

        if not self.select_values(name).entity:
            return

        query = f"""UPDATE maths 
                SET section = ? 
                WHERE LOWER(name) = ?"""
        self.execute_query(query, (section, name.lower()))

    def update_name(self, name: str) -> None:
        """Изменение имени закона в строке базы данных"""

        if not self.select_values(name).entity:
            self.show_error_window()
            return

        query = f"""UPDATE maths 
                SET name = ? 
                WHERE LOWER(name) = ?"""
        self.execute_query(query, (name, name.lower()))

    def delete_values(self, name: str) -> None:
        """Удаление строки в базе данных"""

        if not self.select_values(name).entity:
            self.name_error = True
            return

        query = f"""DELETE FROM maths 
                WHERE LOWER(name) = ?"""
        self.execute_query(query, (name.lower(),))

    def select_values(self, name: str) -> DataEntity:
        """Показ строки из базы данных"""

        query = f"""SELECT * FROM maths 
                WHERE LOWER(name) = ?"""
        result = self.execute_query(query, (name.lower(),))
        return result

    def get_name_list(self) -> list:
        """Вывод списка всех названий законов из базы данных"""

        query = f"""SELECT name FROM maths"""
        with sqlite3.connect('./data/' + user_id + '.db') as db:
            self.cursor = db.cursor()
            result = list(map(lambda x: x[0], self.cursor.execute(query).fetchall()))
            db.commit()
            return result


get_name = False
new_name = False
new_formula = False
new_section = False
delete = False
update_formula = False
update_section = False
check = False
n_name = ''
n_formula = ''
n_section = ''


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global new_name, new_formula, new_section, delete, update_section, update_formula
    global n_name, n_formula, n_section, get_name, check

    if new_name:
        n_name = message.text
        entity = data.select_values(n_name)
        if entity.entity:
            bot.send_message(message.from_user.id,
                             'В базе уже есть данный закон',
                             parse_mode='Markdown')
            new_name = False

        else:
            bot.send_message(message.from_user.id,
                             'Введите формулу закона',
                             parse_mode='Markdown')
            new_name = False
            new_formula = True

    elif new_formula:
        n_formula = message.text
        bot.send_message(message.from_user.id,
                         'Введите раздел математики для закона',
                         parse_mode='Markdown')
        new_formula = False
        new_section = True

    elif new_section:
        n_section = message.text
        new_section = False
        data.add(n_name, n_formula, n_section)
        n_name = ''
        n_formula = ''
        n_section = ''
        bot.send_message(message.from_user.id,
                         'Закон успешно добавлен',
                         parse_mode='Markdown')

    if update_formula:
        if get_name:
            n_name = message.text
            entity = data.select_values(n_name)
            if not entity.entity:
                bot.send_message(message.from_user.id,
                                 'В базе пока нет данного закона',
                                 parse_mode='Markdown')
                update_formula = False
            else:
                bot.send_message(message.from_user.id,
                                 'Введите формулу изменяемого закона',
                                 parse_mode='Markdown')
            get_name = False

        else:
            n_formula = message.text
            data.update_formula(n_name, n_formula)
            n_name = ''
            n_formula = ''
            update_formula = False
            bot.send_message(message.from_user.id,
                             'Закон успешно изменён',
                             parse_mode='Markdown')

    if update_section:
        if get_name:
            n_name = message.text
            entity = data.select_values(n_name)
            if not entity.entity:
                bot.send_message(message.from_user.id,
                                 'В базе пока нет данного закона',
                                 parse_mode='Markdown')
                update_section = False

            else:
                bot.send_message(message.from_user.id,
                                 'Введите раздел математики для изменяемого закона',
                                 parse_mode='Markdown')
            get_name = False

        else:
            n_section = message.text
            data.update_section(n_name, n_section)
            n_name = ''
            n_section = ''
            update_section = False
            bot.send_message(message.from_user.id,
                             'Закон успешно удалён',
                             parse_mode='Markdown')

    if delete:
        n_name = message.text
        entity = data.select_values(n_name)
        if not entity.entity:
            bot.send_message(message.from_user.id,
                             'В базе пока нет данного закона, нажмите на кнопку "Удалить закон" ещё раз',
                             parse_mode='Markdown')

        else:
            data.delete_values(n_name)
            bot.send_message(message.from_user.id,
                             'Закон успешно удалён',
                             parse_mode='Markdown')
        delete = False

    if check:
        n_name = message.text
        entity = data.select_values(n_name)
        if not entity.entity:
            bot.send_message(message.from_user.id,
                             'В базе пока нет данного закона',
                             parse_mode='Markdown')
        else:
            n_name = entity.name
            n_formula = entity.formula
            n_section = entity.section
            ans = 'Название закона: ' + n_name\
                  + '\n' + 'Формула: ' + n_formula\
                  + '\n' + 'Раздел математики: ' + n_section
            bot.send_message(message.from_user.id,
                             ans,
                             parse_mode='Markdown')
        check = False

    elif message.text == 'Поздороваться':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Добавить новый математический закон")
        btn2 = types.KeyboardButton('Удалить закон')
        btn3 = types.KeyboardButton('Изменить формулу закона')
        btn4 = types.KeyboardButton('Изменить раздел математики для закона')
        btn5 = types.KeyboardButton('Посмотреть закон')
        markup.add(btn1, btn2, btn3, btn4, btn5)
        bot.send_message(message.from_user.id, "Привет! Чем могу помочь?", reply_markup=markup)

    elif message.text == 'Добавить новый математический закон':
        bot.send_message(message.from_user.id,
                         'Введите название закона',
                         parse_mode='Markdown')
        new_name = True

    elif message.text == 'Удалить закон':
        bot.send_message(message.from_user.id,
                         'Введите название закона',
                         parse_mode='Markdown')
        delete = True

    elif message.text == 'Изменить формулу закона':
        bot.send_message(message.from_user.id,
                         'Введите название закона',
                         parse_mode='Markdown')
        get_name = True
        update_formula = True

    elif message.text == 'Изменить раздел математики для закона':
        bot.send_message(message.from_user.id,
                         'Введите название закона',
                         parse_mode='Markdown')
        get_name = True
        update_section = True

    elif message.text == 'Посмотреть закон':
        bot.send_message(message.from_user.id,
                         'Введите название закона',
                         parse_mode='Markdown')
        get_name = True
        check = True


bot.polling(none_stop=True, interval=0)
