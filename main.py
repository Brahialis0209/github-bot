import telebot

import ans
import user_opts
from ans import Answers
from user_opts import User, States
import logging
import psycopg2
from flask import Flask, request
import os
import requests
import json


logger = telebot.logger
logger.setLevel(logging.DEBUG)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_URI = os.getenv("DB_URI")
APP_URL = os.getenv("APP_URL")
token = os.environ.get("GITHUB_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)

db_connection = psycopg2.connect(DB_URI, sslmode="require")
db_object = db_connection.cursor()


def update_user_state(user_id, state):
    db_object.execute(f"UPDATE tg_users SET user_state = {state} WHERE tg_user_id = {user_id}")
    db_connection.commit()


def get_user_state(user_id):
    print(user_id)
    db_object.execute(f"SELECT user_state FROM tg_users WHERE tg_user_id = {user_id}")
    result = db_object.fetchone()
    print(result)
    if not result:
        return -1
    return result[0]  # (state,)



@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    username = message.from_user.username
    bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
    db_object.execute(f"SELECT tg_user_id FROM tg_users WHERE tg_user_id = {user_id}")
    result = db_object.fetchone()
    if not result:
        db_object.execute("INSERT INTO tg_users(tg_user_id, tg_username, user_state) VALUES (%s, %s, %s)",
                          (user_id, username, States.S_START))
        db_connection.commit()
        print("GGG1")


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, Answers.reference_ans, parse_mode='Markdown')




# START callback.handlers
def is_user_add(data):
    return User.user_add in data.split(' ')

@bot.callback_query_handler(func=lambda call: is_user_add(call.data))
def query_handler(call):
    print("GGG3")
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Введите имя пользователя:")
    update_user_state(call.message.chat.id, States.S_ADD_USER)



def is_user_control(data):
    return ans.Answers.user_control in data.split(' ')


@bot.callback_query_handler(func=lambda call: is_user_control(call.data))
def query_handler(call):
    print("GGG3")
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=User.ans, reply_markup=user_opts.start_kb_for_user())
    update_user_state(call.message.chat.id, States.S_USER_CONTROL)



def is_user_ali_added(data):
    return ans.Answers.ali_user_added_cal in data.split(' ')

@bot.callback_query_handler(func=lambda call: is_user_ali_added(call.data))
def query_handler(call):
    user_id = call.message.chat.id
    alias = call.data.split(' ')[-1]
    print(user_id)
    print(alias)
    db_object.execute(f"SELECT gh_username, gh_user_avatar FROM gh_users WHERE tg_user_id = '{user_id}' AND tg_alias_user = '{alias}'")
    result = db_object.fetchone()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🔘 Имя: {}\n" \
                                           "🔘 Аватар: {}.".format(result[0], result[1] ))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                     reply_markup=ans.back_to_menu_kb(), text="Меню.")
    # update_user_state(call.message.chat.id, States.S_USER_CONTROL)



def is_back_to_menu(data):
    return ans.Answers.back_to_menu_cal in data.split(' ')

@bot.callback_query_handler(func=lambda call: is_back_to_menu(call.data))
def query_handler(call):
    update_user_state(call.message.chat.id, States.S_START)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=Answers.start_ans, reply_markup=ans.start_kb_for_all())

# END callback.handlers


@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == States.S_ADD_USER)
def user_adding(message):
    print("GGgG2")
    query_url = f"https://api.github.com/users/{message.text}"
    headers = {'Authorization': f'token {token}'}
    r = requests.get(query_url, headers=headers)
    print(r.status_code)
    if r.status_code == 200:
        dict_data = json.loads(r.text)
        gh_username = dict_data['name'] if dict_data['name'] is not None else dict_data['login']
        db_object.execute("INSERT INTO gh_users(tg_user_id , gh_username, gh_user_avatar) VALUES (%s, %s, %s)",
                          (message.from_user.id, gh_username, dict_data['avatar_url']))
        db_connection.commit()
        update_user_state(message.from_user.id, States.S_ALI_USER)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text="Введите alias для нового пользователя.")

    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text="Такого пользователя найти не удалось, попробуйти ввести ник правильно.")



@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == States.S_ALI_USER)
def alias_adding(message):
    user_id = message.from_user.id
    alias = message.text
    print(message.text)
    db_object.execute(f"SELECT gh_username FROM gh_users WHERE tg_alias_user = '{alias}'")
    result = db_object.fetchone()
    print("GGG6")
    if not result:
        db_object.execute(
            f"UPDATE gh_users SET tg_alias_user = '{alias}' WHERE tg_user_id = '{user_id}' AND tg_alias_user IS NULL")
        db_connection.commit()
        print("GGG8")
        update_user_state(message.from_user.id, States.S_ALI_USER_ADDED)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, reply_markup=ans.user_ali_added_kb(alias),
                         text="Пользователь {} добавлен.".format(message.text))
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text="Такой alias уже есть. Введите уникальный.")


@bot.message_handler(content_types=['text'])
def send_text(message):
    print("GGG4")
    bot.send_message(message.chat.id, User.ans, reply_markup=user_opts.start_kb_for_user())


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
