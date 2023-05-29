import os
import requests
from flask import Flask, Response, render_template, request

import telebot
from telebot import types
from api.main import get_variables


TOKEN = os.environ.get('TOKEN')                      # for server app 

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
        json_data = request.get_json()
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        return ''

        
@app.route('/', methods=['GET'])
def index():
    return render_template("/index.html") 


