import os
import requests
from flask import Flask, Response, render_template, request

import telebot
from telebot import types
from api.main import get_variables


TOKEN = os.environ.get('TOKEN')                      # for server app 

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)


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

        bot.send_message(message.chat.id, """Бот готов к работе. Ниже последние настройки постинга изображений.
        Воспользуйтесь кнопками меню для дальнейшей работы""", reply_markup=keyboard)
        bot.send_message(message.chat.id, f'{variables}')
    except:
        bot.send_message(message.chat.id,'User settings not found.\nPlease enter request parameters for image reposting')
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Выберете необходимое действие")
 
        bot.send_message(message.chat.id, """Бот готов к работе. Ниже последние настройки постинга изображений. 
                        Воспользуйтесь кнопками меню для дальнейшей работы.""", reply_markup=keyboard)
        bot.send_message(message.chat.id, f'{variables}')
