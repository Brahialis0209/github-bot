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
from telebot import types


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
    db_object.execute(f"SELECT user_state FROM tg_users WHERE tg_user_id = {user_id}")
    result = db_object.fetchone()
    if not result:
        return -1
    return result[0]  # (state,)



@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    username = message.from_user.username
    db_object.execute(f"SELECT tg_user_id FROM tg_users WHERE tg_user_id = {user_id}")
    result = db_object.fetchone()
    if not result:
        db_object.execute("INSERT INTO tg_users(tg_user_id, tg_username, user_state) VALUES (%s, %s, %s)",
                          (user_id, username, States.S_START))
        db_connection.commit()
        bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
    else:
        if get_user_state(user_id) == States.S_START:
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
        elif get_user_state(user_id) == States.S_USER_CONTROL:
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state(message.chat.id, States.S_START)
        elif get_user_state(user_id) == States.S_CHOOSE_USER:
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state(message.chat.id, States.S_START)

        elif get_user_state(user_id) == States.S_ADD_USER:
            #  we enter start or any text and losed username or alias, therefore need to remove row in gh_userd with alias == null
            db_object.execute(
                f"DELETE FROM gh_users  WHERE tg_user_id = '{user_id}' AND tg_alias_user IS NULL")
            db_connection.commit()
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state(message.chat.id, States.S_START)
        elif get_user_state(user_id) == States.S_ALI_USER_ENTER:
            #  we enter start or any text and losed username or alias, therefore need to remove row in gh_userd with alias == null
            db_object.execute(
                f"DELETE FROM gh_users  WHERE tg_user_id = '{user_id}' AND tg_alias_user IS NULL")
            db_connection.commit()
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state(message.chat.id, States.S_START)
        elif get_user_state(user_id) == States.S_ALI_USER_ADDED:
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state(message.chat.id, States.S_START)



# START callback.handlers

# "back" when we choosen alias
@bot.callback_query_handler(func=lambda call: get_user_state(call.message.chat.id) == States.S_CHOOSE_USER
                                              and call.data.split(" ")[-1] == user_opts.User.back_cal)
def query_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=User.ans, reply_markup=user_opts.start_kb_for_user())
    update_user_state(call.message.chat.id, States.S_USER_CONTROL)


#  we pick alias from our list
@bot.callback_query_handler(func=lambda call: get_user_state(call.message.chat.id) == States.S_CHOOSE_USER
                                              and call.data.split(" ")[-1] != user_opts.User.back_cal)
def query_handler(call):
    alias = call.data.split(" ")[0]
    user_id = call.message.chat.id
    db_object.execute(
        f"SELECT gh_username, gh_user_avatar, gh_user_url FROM gh_users WHERE tg_user_id = '{user_id}' AND tg_alias_user = '{alias}'")
    result = db_object.fetchone()
    name = result[0]
    avatar = result[1]
    url = result[2]
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🔘 Имя: {}\n" \
 \
                                                                                                 "🔘 Ссылка на пользователя: {}.".format(
        name, url),
                          reply_markup=ans.back_to_menu_kb())
    update_user_state(call.message.chat.id, States.S_START)



def is_user_choose(data):
    return User.user_choice in data.split(' ')
#  we pick check history of aliases
@bot.callback_query_handler(func=lambda call: is_user_choose(call.data))
def query_handler(call):
    db_object.execute(
        f"SELECT tg_alias_user FROM gh_users WHERE tg_user_id = '{call.message.chat.id}'")
    result = db_object.fetchall()
    len_hist = len(result)
    if len_hist == 0:
        mark = types.InlineKeyboardMarkup()
        mark.row(types.InlineKeyboardButton(User.back_inf,
                                            callback_data=" " + User.back_cal))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Список сохранённых alias пуст. Добавьте нового пользователя.",
                              reply_markup=mark)

    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=User.ans, reply_markup=user_opts.aliases_kb_for_user(db_object, call.message.chat.id))
    update_user_state(call.message.chat.id, States.S_CHOOSE_USER)


def is_user_add(data):
    return User.user_add in data.split(' ')
#  we pick add user
@bot.callback_query_handler(func=lambda call: is_user_add(call.data))
def query_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Введите имя пользователя:")
    update_user_state(call.message.chat.id, States.S_ADD_USER)



def is_user_control(data):
    return ans.Answers.user_control in data.split(' ')
#  we pick user control (1 step)
@bot.callback_query_handler(func=lambda call: is_user_control(call.data))
def query_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=User.ans, reply_markup=user_opts.start_kb_for_user())
    update_user_state(call.message.chat.id, States.S_USER_CONTROL)



def is_user_ali_added(data):
    return ans.Answers.ali_user_added_cal in data.split(' ')
#  we enter give me info about user
@bot.callback_query_handler(func=lambda call: is_user_ali_added(call.data))
def query_handler(call):
    user_id = call.message.chat.id
    alias = call.data.split(' ')[-1]
    db_object.execute(f"SELECT gh_username, gh_user_avatar, gh_user_url FROM gh_users WHERE tg_user_id = '{user_id}' AND tg_alias_user = '{alias}'")
    result = db_object.fetchone()
    name = result[0]
    avatar = result[1]
    url = result[2]
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🔘 Имя: {}\n" \
                                                                                                 
                                                                                             "🔘 Ссылка на пользователя: {}.".format(name, url),
                          reply_markup=ans.back_to_menu_kb())


def is_back_to_menu(data):
    return ans.Answers.back_to_menu_cal in data.split(' ')
#  pick back to main menu
@bot.callback_query_handler(func=lambda call: is_back_to_menu(call.data))
def query_handler(call):
    update_user_state(call.message.chat.id, States.S_START)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=Answers.start_ans, reply_markup=ans.start_kb_for_all())
# END callback.handlers


# START MESS HANDLERS
#  we enter user_name
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == States.S_ADD_USER)
def user_adding(message):
    query_url = f"https://api.github.com/users/{message.text}"
    headers = {'Authorization': f'token {token}'}
    r = requests.get(query_url, headers=headers)
    if r.status_code == 200:
        dict_data = json.loads(r.text)
        name = dict_data['login']
        db_object.execute(f"SELECT tg_user_id, tg_alias_user FROM gh_users WHERE tg_user_id = '{message.from_user.id}' AND gh_username = '{name}'")
        result = db_object.fetchall()
        if len(result) != 0:
            alias = str(result[0][1]).replace(" ", "")
            bot.send_message(chat_id=message.chat.id,
                             text="Такой пользователь уже существует в вашем сохранённом списке под псевдонимом: {}. Введите другой ник.".format(alias))
        else:
            dict_data = json.loads(r.text)
            gh_username = dict_data['name'] if dict_data['name'] is not None else dict_data['login']
            db_object.execute("INSERT INTO gh_users(tg_user_id , gh_username, gh_user_avatar, gh_user_url) VALUES (%s, %s, %s, %s)",
                              (message.from_user.id, gh_username, dict_data['avatar_url'], dict_data['html_url']))
            db_connection.commit()
            update_user_state(message.from_user.id, States.S_ALI_USER_ENTER)
            bot.send_message(chat_id=message.chat.id,
                                  text="Введите alias для нового пользователя.")

    else:
        bot.send_message(chat_id=message.chat.id,
                              text="Такого пользователя найти не удалось, попробуйти ввести ник правильно.")


#  we enter alias for user
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == States.S_ALI_USER_ENTER)
def alias_adding(message):
    user_id = message.from_user.id
    alias = message.text
    db_object.execute(f"SELECT gh_username FROM gh_users WHERE tg_alias_user = '{alias}'")
    result = db_object.fetchone()
    if not result:
        db_object.execute(
            f"UPDATE gh_users SET tg_alias_user = '{alias}' WHERE tg_user_id = '{user_id}' AND tg_alias_user IS NULL")
        db_connection.commit()
        update_user_state(message.from_user.id, States.S_ALI_USER_ADDED)
        bot.send_message(chat_id=message.chat.id, reply_markup=ans.user_ali_added_kb(alias),
                         text="Пользователь {} добавлен.".format(message.text))
    else:
        bot.send_message(chat_id=message.chat.id,
                              text="Такой alias уже есть. Введите уникальный.")

# END MESS HANDLERS




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
