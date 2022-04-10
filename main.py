import telebot
import user_opts
from ans import Answers
from user_opts import User
import logging
import psycopg2
from config import *
from flask import Flask, request
import os


bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)
logger = telebot.logger
logger.setLevel(logging.DEBUG)



@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, Answers.start_ans, reply_markup=Answers.main_markup, parse_mode='markdown')


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, Answers.reference_ans, parse_mode='Markdown')



@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text == Answers.user_inf:
        bot.send_message(message.chat.id, User.ans, reply_markup=user_opts.start_kb_for_user())



def is_user_add(data):
    return User.user_add in data.split(' ')



@bot.callback_query_handler(func=lambda call: is_user_add(call.data))
def query_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Введите ссылку на пользователя:")





@server.route(f"/{BOT_TOKEN}", methods=["POST"])
def redirect_message():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

