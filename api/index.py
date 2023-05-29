import os
import requests
from flask import Flask, Response, render_template, request

import telebot
from telebot import types






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
    bot.send_message(message.chat.id, "Эта команда не поддерживается ботом. Узнать список допустимых команд можно используя команду /help")

