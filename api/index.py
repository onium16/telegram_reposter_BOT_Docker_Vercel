# import subprocess

# subprocess.run(["pip", "install", "flask"])
# subprocess.run(["pip", "install", "requests"])
# subprocess.run(["pip", "install", "pyTelegramBotAPI"])
# subprocess.run(["pip", "install", "apscheduler"])
# subprocess.run(["pip", "install", "psycopg2"])


import re
import os
import time as time_pause
from random import randint

import telebot
from telebot import types
from flask import Flask, request, Response, render_template

from DuckduckGo_parser import DuckDuckGoImageParcer
from main import get_variables
from db_worker import DBworker
from saver_for_parcer import Save_to_DB_or_FILE
# from _config import TOKEN                              # for local app

from apscheduler.schedulers.background import BackgroundScheduler
import datetime
from datetime import datetime, time


TOKEN = os.environ.get('TOKEN')                      # for server app 

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# keyboard button names
text_b_start_settings = "Приступить к настройке"
text_b_save_last_settings = "Продолжить с текущими настройками"
text_b_cancel = '/cancel'
text_b_save_settings = 'Сохранить настройки'
text_b_start_posting = 'Запустить постинг'
text_b_stop_posting = 'Остановить постинг'

# buttons keyboard
b_start_settings = types.KeyboardButton(text_b_start_settings)
b_save_last_settings = types.KeyboardButton(text_b_save_last_settings)
b_cancel = types.KeyboardButton(text_b_cancel)
b_save_settings = types.KeyboardButton(text_b_save_settings)
b_start_posting = types.KeyboardButton(text_b_start_posting)
b_stop_posting = types.KeyboardButton(text_b_stop_posting)


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'POST':
        if request.headers.get('content-type') == 'application/json':
            json_data = request.get_json()
            update = telebot.types.Update.de_json(json_data)
            bot.process_new_updates([update])
            return ''
        else:
            return Response(status=403)
        
    elif request.method == 'GET':
        return render_template("/webhook.html") 
    else:
        return "Неподдерживаемый метод запроса"


@app.route('/', methods=['GET'])
def index():
    return render_template("/index.html") 


@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        variables = get_variables(message.from_user.id)
        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Выберете необходимое действие")
        keyboard.row(b_start_settings, b_save_last_settings)
        keyboard.add(b_cancel)
        bot.send_message(message.chat.id, """Бот готов к работе. Ниже последние настройки постинга изображений.
        Воспользуйтесь кнопками меню для дальнейшей работы""", reply_markup=keyboard)
        bot.send_message(message.chat.id, f'{variables}')
    except:
        bot.send_message(message.chat.id,'User settings not found.\nPlease enter request parameters for image reposting')
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Выберете необходимое действие")
        keyboard.row(b_start_settings)
        keyboard.add(b_cancel)
        bot.send_message(message.chat.id, """Бот готов к работе. Ниже последние настройки постинга изображений. 
                        Воспользуйтесь кнопками меню для дальнейшей работы.""", reply_markup=keyboard)
        bot.send_message(message.chat.id, f'{variables}')


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, "Сам себе помоги")


@bot.message_handler(commands=['cancel'])
def send_cancel(message):
    bot.send_message(message.chat.id, "Операции отменены. Для возобновления работы выберете команду '/start'")


@bot.message_handler(func=lambda message: message.text == text_b_start_settings)
def handle_start_command(message):
    # Отправка сообщения с просьбой ввести название группы
    msg = bot.send_message(message.chat.id, "Введите название группы:")
    bot.register_next_step_handler(msg, process_group_name)

def process_group_name(message):
    global group_name
    group_name = message.text

    if bool(re.match(r'@[\w]{5,}', group_name)) == True:
        # Если название группы введено верно, продолжить обработку
        msg = bot.send_message(message.chat.id, "Введите количество картинок для репостинга:")
        bot.register_next_step_handler(msg, process_image_count)
    else:
        # Если название группы введено неверно, повторить запрос
        bot.send_message(message.chat.id, "Введите корректное название группы (должно начинаятся с @ и иметь длинну не менее пяти символов):")
        bot.register_next_step_handler(message, process_group_name)

def process_image_count(message):
    global image_count
    try:
        image_count = int(message.text)
        if image_count > 0:
            # Если количество картинок введено верно, продолжить обработку
            msg = bot.send_message(message.chat.id, "Укажите время срабатывания постинга (пример 23:59:59):")
            bot.register_next_step_handler(msg, process_timescript)
        else:
            # Если количество картинок введено неверно, повторить запрос
            bot.send_message(message.chat.id, "Введите корректное количество картинок (больше 0):")
            bot.register_next_step_handler(message, process_image_count)
    except ValueError:
        # Если введено некорректное значение, повторить запрос
        bot.send_message(message.chat.id, "Введите корректное количество картинок (целое число):")
        bot.register_next_step_handler(message, process_image_count)

def process_timescript(message):
    global timescript
    try:
        timescript = message.text
        if  bool(re.match(r'^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$', timescript)) == True:
            # Если время введено верно, продолжить обработку
            msg = bot.send_message(message.chat.id, "Напишите ключевые слова для парсинга, при парсинге они быдут выбирать рандомно:")
            bot.register_next_step_handler(msg, process_list_parcer)
        else:
            # Если время введено неверно, повторить запрос
            bot.send_message(message.chat.id, "Введите корректное время (11:02:33, в 24 часовом формате):")
            bot.register_next_step_handler(message, process_timescript)
    except ValueError:
            # Если введено некорректное значение, повторить запрос
            bot.send_message(message.chat.id, "Введите корректное время (11:02:33, в 24 часовом формате). Я в тебя верю:")
            bot.register_next_step_handler(message, process_timescript)

def process_list_parcer(message):
    global list_parcer
    try:
        list_parcer = message.text
        if  bool(re.match(r'^([\w\d\s]+(?:,[\w\d\s]+){0,9})$', list_parcer)) == True:
            # Если список введен верно, продолжить обработку
            bot.send_message(message.chat.id, 
                             f"""User_ID: {message.from_user.id},\n
                             Название группы: {group_name},\n
                             "Количество картинок для репостинга: {image_count},\n
                             Время срабатывания скрипта: {timescript},\n
                             Ключевые словa/выражения: {list_parcer},\n
                             """)

            bot.send_message(message.chat.id, "Данные сохранены")
            db = DBworker()
            db.setup_settings(message.from_user.id, image_count, re.split(r'\s*,\s*', list_parcer), group_name, timescript)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Выберете необходимое действие")
            keyboard.row(b_start_posting)
            keyboard.add(b_cancel)
            bot.send_message(message.chat.id, """Выберите следующие действия""", reply_markup=keyboard)
            # Дальнейшая обработка
        else:
            # Если  список введен неверно, повторить запрос
            bot.send_message(message.chat.id, "Введите корректные данные. Напишите от 1 до 10 ключевых слов для парсинга (могут содержать буквы и цифры), раздели их запятыми:")
            bot.register_next_step_handler(message, process_list_parcer)
    except ValueError:
            # Если список введен некорректно, повторить запрос
            bot.send_message(message.chat.id, "Введите корректные данные. Напишите от 1 до 10 ключевых слов для парсинга (могут содержать буквы и цифры), раздели их запятыми. Я в тебя верю:")
            bot.register_next_step_handler(message, process_list_parcer)

@bot.callback_query_handler(func=lambda call: call.data == "send_data")
def handle_send_data_query(call):
    if group_name and image_count and timescript and list_parcer:
        bot.send_message(call.message.chat.id, f"Название группы/канала: {group_name}")
        bot.send_message(call.message.chat.id, f"Количество картинок для репостинга: {image_count}")
        bot.send_message(call.message.chat.id, f"Время срабатывания скрипта: {timescript}")
        bot.send_message(call.message.chat.id, f"Ключевые словa/выражения: {list_parcer}")
        
        # Добавьте дальнейшую обработку данных
    else:
        bot.send_message(call.message.chat.id, "Введите /start, чтобы настроить репостинг")

    # остановить парсинг

@bot.message_handler(func=lambda message: message.text == 'Продолжить с текущими настройками')
def countinue_current_settings(message, content_types = ['text']):
    bot.send_message(message.chat.id, "все срабатывает")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.row(b_start_posting, b_stop_posting)
    keyboard.add(b_cancel)
    bot.send_message(message.chat.id, "Выберете необходимое действие:",
                    reply_markup=keyboard)

    # bot.send_message(message.chat.id, "Эта команда 'Запустить постинг'")

#//////////////////////////////////////////////////////////////

def parse_and_send_messages(message):
    bot.send_message(message.chat.id, "Постинг запущен. Для обработки потребуется немного времени. Если изображения не получены проверьте настройки бота группы/канала.")
    link_for_send_telegram, ID, NUMBER, LIST_FOR_SEARCH, GROUP_CHANNEL, TIMESCRIPT = start_parcer_and_saver_links(message.from_user.id)
    time_pause.sleep(0.5)
    # print(link_for_send_telegram)
    try:
        for link in link_for_send_telegram:
            bot.send_photo(chat_id = GROUP_CHANNEL, photo= link)
            print(link, '- отправленна')
            time_pause.sleep(0.5)
        link_for_send_telegram = []
    except:
        bot.send_message(message.chat.id, "Произошла ошибка при отправки ссылки.")

        bot.register_next_step_handler(message, parse_and_send_messages)

scheduler = None  # Глобальная переменная для хранения планировщика

@bot.message_handler(func=lambda message: message.text == text_b_start_posting)
def start_posting_handler(message):
    global scheduler
    TIMESCRIPT = get_variables(message.from_user.id)[-1]
    bot.send_message(message.chat.id, f'Запущена операция постинга. Запланированное время топравки сообщения {TIMESCRIPT}')
    scheduler = BackgroundScheduler()
    # Преобразование строки TIMESCRIPT в объект time
    time_parts = TIMESCRIPT.split(":")
    time_script = time(int(time_parts[0]), int(time_parts[1]), int(time_parts[2]))

    # Установка ежедневного срабатывания с указанным временем начала
    
    # scheduler.add_job(parse_and_send_messages, trigger='interval', days=1, start_date=datetime.now().date(), start_time=time_script, args=[GROUP_CHANNEL, link_for_send_telegram])

    # test срабатывание каждую минуту
    scheduler.add_job(parse_and_send_messages, trigger='interval', minutes=2, start_date=datetime.now().date(), args=[message]) 


    scheduler.start()
    bot.send_message(message.chat.id, 'Планировщик запущен')

@bot.message_handler(func=lambda message: message.text == text_b_stop_posting)
def stop_posting_handler(message):
    global scheduler
    bot.send_message(message.chat.id, 'Операция постинга остановлена. Введите или нажмите /start, для осуществления настроек, или откройте клавиатуру и запустите постинг с прежними настройками.')
    if scheduler:
        scheduler.shutdown()

@bot.message_handler(content_types=['text'])
def send_commands_not_supported(message, content_types = []):
    bot.send_message(message.chat.id, "Эта команда не поддерживается ботом. Узнать список допустимых команд можно используя команду /help")

class RequestData():  # random keyword from LIST_FOR_SEARCH param
    '''The class contains a method 'GET_KEYWORD' that receives a list of string data, 
       and using the random library, receives a random element of the list. 
       In this case KEYWORD'''
    def get_keyword(self, listForSearch):
        keyword = listForSearch[randint(0, len(listForSearch)-1)]
        return keyword

def start_parcer_and_saver_links(id_user):
    ID, NUMBER, LIST_FOR_SEARCH, GROUP_CHANNEL, TIMESCRIPT = get_variables(id_user)
    keyword = RequestData().get_keyword(LIST_FOR_SEARCH)
    print(keyword)
    Duck_parsing = DuckDuckGoImageParcer()
    save_link = Save_to_DB_or_FILE()
    link_for_send_telegram = save_link.save_to_db(
        id_user=ID,
        number=NUMBER,
        list_for_search=LIST_FOR_SEARCH,
        keyword=keyword,
        group_channel=GROUP_CHANNEL,
        timescript=TIMESCRIPT,
        parcer=Duck_parsing.parcingimage
    )
    return link_for_send_telegram, ID, NUMBER, LIST_FOR_SEARCH, GROUP_CHANNEL, TIMESCRIPT


if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')


