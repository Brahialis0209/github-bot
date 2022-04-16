import telebot
import user_opts
from ans import Answers
from user_opts import User, States
import logging
import psycopg2
# from config import *
from flask import Flask, request
import os

logger = telebot.logger
logger.setLevel(logging.DEBUG)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_URI = os.getenv("DB_URI")
APP_URL = os.getenv("APP_URL")

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)

db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()


def update_user_state(user_id, state):
    db_object.execute(f"UPDATE tg_users SET user_state = {state} WHERE tg_user_id = {user_id}")
    db_connection.commit()


def get_user_state(user_id):
    db_object.execute(f"SELECT user_state FROM tg_users WHERE tg_user_id = {user_id}")
    result = db_object.fetchone()
    if not result:
        return -1
    return result[0]  # (state,)


@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    username = message.from_user.username
    bot.send_message(message.chat.id, Answers.start_ans, reply_markup=Answers.main_markup, parse_mode='markdown')
    db_object.execute(f"SELECT tg_user_id FROM tg_users WHERE tg_user_id = {user_id}")
    result = db_object.fetchone()
    if not result:
        db_object.execute("INSERT INTO tg_users(tg_user_id, tg_username, user_state) VALUES (%s, %s, %s)", (user_id, username, States.S_START))
        db_connection.commit()
        print("GGG1")



@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, Answers.reference_ans, parse_mode='Markdown')




def is_user_add(data):
    return User.user_add in data.split(' ')



@bot.callback_query_handler(func=lambda call: is_user_add(call.data))
def query_handler(call):
    print("GGG3")
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Введите ссылку на пользователя:")
    update_user_state(call.message.chat.id, States.S_ADD_USER)


@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == States.S_ADD_USER)
def user_adding(message):
    print("GGG2")
    bot.send_message(message.chat.id, text=message.text)
    # dbworker.set_state(message.chat.id, config.States.S_ENTER_AGE.value)



@bot.message_handler(content_types=['text'])
def send_text(message):
    print("GGG4")
    if message.text == Answers.user_inf:
        bot.send_message(message.chat.id, User.ans, reply_markup=user_opts.start_kb_for_user())
        update_user_state(message.from_user.id, States.S_USER_CONTROL)


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

