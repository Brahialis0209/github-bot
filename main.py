import telebot
import ans
import user_opts
from ans import Answers
from user_opts import User, States
import logging
from flask import Flask, request
import os
import requests
import json
from telebot import types
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from data_models import Base, TgUser, GitHubUsers, GitHubRepos, GitHubPullRequest


logger = telebot.logger
logger.setLevel(logging.DEBUG)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_URI = os.getenv("DB_URI")
APP_URL = os.getenv("APP_URL")
token = os.environ.get("GITHUB_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)

# hack to transform default postgres DB_URI into SqlAlchemy-suitable
db_uri_fixed = DB_URI
if db_uri_fixed.startswith("postgres://"):
    db_uri_fixed = db_uri_fixed.replace("postgres://", "postgresql://", 1)

db_engine = create_engine(db_uri_fixed, echo=True)
Base.metadata.create_all(db_engine)


def update_user_state(user_id, state):
    session = Session(db_engine)
    update_user_state_with_session(user_id, state, session)
    finish_session(session)


def update_user_state_with_session(user_id, state, session: Session):
    tg_user = session.query(TgUser).filter_by(tg_user_id=user_id).first()
    if tg_user is not None:
        tg_user.user_state = state
    session.commit()
    session.flush()


def get_user_state(user_id):
    session = Session(db_engine)
    get_user_state_with_session(user_id, session)
    finish_session(session)


def get_user_state_with_session(user_id, session: Session):
    tg_user = session.query(TgUser).filter_by(tg_user_id=int(user_id)).first()
    print(-1 if tg_user is None else tg_user.user_state)
    return -1 if tg_user is None else tg_user.user_state


def delete_null_alias_from_users(user_id, session: Session):
    # Use "==" instead of "is" in comparison with None to properly construct SQL query
    null_alias = session.query(GitHubUsers).filter_by(
        tg_user_id=user_id,
        tg_alias_user=None  # noqa
    ).first()
    if null_alias is not None:
        session.delete(null_alias)
        session.commit()
        session.flush()


def delete_null_alias_from_repos(user_id, session: Session):
    # Use "==" instead of "is" in comparison with None to properly construct SQL query
    null_alias = session.query(GitHubRepos).filter_by(
        tg_user_id=user_id,
        tg_alias_repos=None  # noqa
    ).first()
    if null_alias is not None:
        session.delete(null_alias)
        session.commit()
        session.flush()


def delete_null_alias_from_pull_requests(user_id, session: Session):
    # Use "==" instead of "is" in comparison with None to properly construct SQL query
    null_alias = session.query(GitHubPullRequest).filter_by(
        tg_user_id=user_id,
        tg_alias_pr=None  # noqa
    ).first()
    if null_alias is not None:
        session.delete(null_alias)
        session.commit()
        session.flush()


def finish_session(session: Session):
    session.commit()
    session.flush()
    session.close()


@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    username = message.from_user.username
    # Find out if there's a new user or he/she has been already registered
    session = Session(db_engine)
    current_user = session.query(TgUser).filter_by(tg_user_id=int(user_id)).first()
    if current_user is None:
        # User is not in the database -> add user to the database and set initial state
        current_user = TgUser(tg_user_id=user_id, tg_username=username, user_state=States.S_START)
        session.add(current_user)
        session.commit()
        # Greet
        bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
    else:
        # User has already been registered in the database so we act up to status of the user
        usr_status = get_user_state_with_session(user_id, session)
        if usr_status == States.S_START:
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())

        # user options
        elif usr_status == States.S_USER_CONTROL:
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state_with_session(message.chat.id, States.S_START, session)
        elif usr_status == States.S_CHOOSE_USER:
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state_with_session(message.chat.id, States.S_START, session)

        elif usr_status == States.S_ADD_USER:
            #  we enter start or any text and losed username or alias,
            #  therefore need to remove row in gh_userd with alias == null
            delete_null_alias_from_users(user_id, session)
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state_with_session(message.chat.id, States.S_START, session)
        elif usr_status == States.S_ALI_USER_ENTER:
            #  we enter start or any text and losed username or alias,
            #  therefore need to remove row in gh_userd with alias == null
            delete_null_alias_from_users(user_id, session)
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state_with_session(message.chat.id, States.S_START, session)
        elif usr_status == States.S_ALI_USER_ADDED:
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state_with_session(message.chat.id, States.S_START, session)

        # repos options
        elif usr_status == States.S_REPOS_CONTROL:
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state_with_session(message.chat.id, States.S_START, session)
        elif usr_status == States.S_CHOOSE_REPOS:
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state_with_session(message.chat.id, States.S_START, session)

        elif usr_status == States.S_ADD_REPOS:
            #  we enter start or any text and losed repository name or alias,
            #  therefore need to remove row in gh_userd with alias == null
            delete_null_alias_from_repos(user_id, session)
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state_with_session(message.chat.id, States.S_START, session)
        elif usr_status == States.S_ALI_REPOS_ENTER:
            #  we enter start or any text and losed repository name or alias,
            #  therefore need to remove row in gh_userd with alias == null
            delete_null_alias_from_repos(user_id, session)
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state_with_session(message.chat.id, States.S_START, session)
        elif usr_status == States.S_ALI_REPOS_ADDED:
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state_with_session(message.chat.id, States.S_START, session)

        # pr options
        elif usr_status == States.S_PR_CONTROL:
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state_with_session(message.chat.id, States.S_START, session)
        elif usr_status == States.S_CHOOSE_PR:
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state_with_session(message.chat.id, States.S_START, session)

        elif usr_status == States.S_ADD_PR:
            #  we enter start or any text and losed repository name or alias,
            #  therefore need to remove row in gh_userd with alias == null
            delete_null_alias_from_pull_requests(user_id, session)
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state_with_session(message.chat.id, States.S_START, session)
        elif usr_status == States.S_ALI_PR_ENTER:
            #  we enter start or any text and losed repository name or alias,
            #  therefore need to remove row in gh_userd with alias == null
            delete_null_alias_from_pull_requests(user_id, session)
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state_with_session(message.chat.id, States.S_START, session)
        elif usr_status == States.S_ALI_PR_ADDED:
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state_with_session(message.chat.id, States.S_START, session)
        else:
            bot.send_message(message.chat.id, Answers.start_ans, reply_markup=ans.start_kb_for_all())
            update_user_state_with_session(message.chat.id, States.S_START, session)
    finish_session(session)


# ---------------------------------------------------------------------------------------------
# START callback.handlers
# -------------------------------
# "back" when we have chosen user control options
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_USER_CONTROL
        and call.data.split(" ")[-1] == user_opts.User.back_cal))
def query_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=Answers.start_ans, reply_markup=ans.start_kb_for_all())
    update_user_state(call.message.chat.id, States.S_START)


# "back" when we have chosen repos control options
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_REPOS_CONTROL
        and call.data.split(" ")[-1] == user_opts.User.back_cal))
def query_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=Answers.start_ans, reply_markup=ans.start_kb_for_all())
    update_user_state(call.message.chat.id, States.S_START)


# "back" when we have chosen pr control options
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_PR_CONTROL
        and call.data.split(" ")[-1] == user_opts.User.back_cal))
def query_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=Answers.start_ans, reply_markup=ans.start_kb_for_all())
    update_user_state(call.message.chat.id, States.S_START)


#  we pick user control (1 step)
def is_user_control(data):
    return ans.Answers.user_control in data.split(' ')


@bot.callback_query_handler(func=lambda call: is_user_control(call.data))
def query_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=User.ans, reply_markup=user_opts.start_kb_for_user())
    update_user_state(call.message.chat.id, States.S_USER_CONTROL)


#  we pick repos control (1 step)
def is_repos_control(data):
    return ans.Answers.repos_control in data.split(' ')


@bot.callback_query_handler(func=lambda call: is_repos_control(call.data))
def query_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=User.ans, reply_markup=user_opts.start_kb_for_repos())
    update_user_state(call.message.chat.id, States.S_REPOS_CONTROL)


#  we pick pr control (1 step)
def is_pr_control(data):
    return ans.Answers.pr_control in data.split(' ')


@bot.callback_query_handler(func=lambda call: is_pr_control(call.data))
def query_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=User.ans, reply_markup=user_opts.start_kb_for_pr())
    update_user_state(call.message.chat.id, States.S_PR_CONTROL)


# -------------------------------
# "back" when we choose user alias from history
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_CHOOSE_USER
        and call.data.split(" ")[-1] == user_opts.User.back_cal))
def query_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=User.ans, reply_markup=user_opts.start_kb_for_user())
    update_user_state(call.message.chat.id, States.S_USER_CONTROL)


# "back" when we choose repos alias from history
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_CHOOSE_REPOS
        and call.data.split(" ")[-1] == user_opts.User.back_cal))
def query_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=User.ans, reply_markup=user_opts.start_kb_for_repos())
    update_user_state(call.message.chat.id, States.S_REPOS_CONTROL)


# "back" when we choose pr alias from history
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_CHOOSE_PR
        and call.data.split(" ")[-1] == user_opts.User.back_cal))
def query_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=User.ans, reply_markup=user_opts.start_kb_for_pr())
    update_user_state(call.message.chat.id, States.S_PR_CONTROL)


#  we pick check history of user aliases
def is_user_choose(data):
    return User.user_choice in data.split(' ')


@bot.callback_query_handler(func=lambda call: is_user_choose(call.data))
def query_handler(call):
    session = Session(db_engine)
    github_user_aliases = session.query(GitHubUsers.tg_alias_user).filter_by(
        tg_user_id=call.message.chat.id
    ).all()
    if github_user_aliases is None or len(github_user_aliases) == 0:
        mark = types.InlineKeyboardMarkup()
        mark.row(types.InlineKeyboardButton(User.back_inf,
                                            callback_data=" " + User.back_cal))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Список сохранённых alias пуст. Добавьте нового пользователя.",
                              reply_markup=mark)

    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=User.user_history_aliases_ans,
                              reply_markup=user_opts.aliases_kb_for_user(call.message.chat.id, session))
    update_user_state_with_session(call.message.chat.id, States.S_CHOOSE_USER, session)
    finish_session(session)


#  we pick check history of repos aliases
def is_repos_choose(data):
    return User.repos_choice in data.split(' ')


@bot.callback_query_handler(func=lambda call: is_repos_choose(call.data))
def query_handler(call):
    session = Session(db_engine)
    repos_aliases = session.query(GitHubRepos.tg_alias_repos).filter_by(
        tg_user_id=call.message.chat.id
    ).all()
    if repos_aliases is None or len(repos_aliases) == 0:
        mark = types.InlineKeyboardMarkup()
        mark.row(types.InlineKeyboardButton(User.back_inf,
                                            callback_data=" " + User.back_cal))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Список сохранённых alias пуст. Добавьте новый репозиторий.",
                              reply_markup=mark)

    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=User.repos_history_aliases_ans,
                              reply_markup=user_opts.aliases_kb_for_repos(call.message.chat.id, session))
    update_user_state_with_session(call.message.chat.id, States.S_CHOOSE_REPOS, session)
    finish_session(session)


#  we pick check history of repos aliases
def is_pr_choose(data):
    return User.pr_choice in data.split(' ')


@bot.callback_query_handler(func=lambda call: is_pr_choose(call.data))
def query_handler(call):
    session = Session(db_engine)
    pr_aliases = session.query(GitHubPullRequest.tg_alias_pr).filter_by(
        tg_user_id=call.message.chat.id
    ).all()
    if pr_aliases is None or len(pr_aliases) == 0:
        mark = types.InlineKeyboardMarkup()
        mark.row(types.InlineKeyboardButton(User.back_inf,
                                            callback_data=" " + User.back_cal))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Список сохранённых alias пуст. Добавьте новый pull request.",
                              reply_markup=mark)

    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=User.pr_history_aliases_ans,
                              reply_markup=user_opts.aliases_kb_for_pr(call.message.chat.id, session))
    update_user_state_with_session(call.message.chat.id, States.S_CHOOSE_PR, session)
    finish_session(session)


# -------------------------------
# "back" when we choose add new user
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_ADD_USER
        and call.data.split(" ")[-1] == user_opts.User.back_cal))
def query_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=User.ans, reply_markup=user_opts.start_kb_for_user())
    update_user_state(call.message.chat.id, States.S_USER_CONTROL)


# "back" when we choose add new repos
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_ADD_REPOS
        and call.data.split(" ")[-1] == user_opts.User.back_cal))
def query_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=User.ans, reply_markup=user_opts.start_kb_for_repos())
    update_user_state(call.message.chat.id, States.S_REPOS_CONTROL)


# "back" when we choose add new pr
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_ADD_PR
        and call.data.split(" ")[-1] == user_opts.User.back_cal))
def query_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=User.ans, reply_markup=user_opts.start_kb_for_pr())
    update_user_state(call.message.chat.id, States.S_PR_CONTROL)


#  we pick add user
def is_user_add(data):
    return User.user_add in data.split(' ')


@bot.callback_query_handler(func=lambda call: is_user_add(call.data))
def query_handler(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          reply_markup=ans.back_to_previous_kb(),
                          text="Введите имя пользователя:")
    update_user_state(call.message.chat.id, States.S_ADD_USER)


#  we pick add repos
def is_repos_add(data):
    return User.repos_add in data.split(' ')


@bot.callback_query_handler(func=lambda call: (
        is_repos_add(call.data)
        or (
                get_user_state(call.message.chat.id) == States.S_LOOK_USER_REPOS
                and call.data.split(" ")[-1] == user_opts.User.back_cal)
)
                            )
def query_handler(call):
    session = Session(db_engine)
    github_user_aliases = session.query(GitHubUsers.tg_alias_user).filter_by(
        tg_user_id=call.message.chat.id
    ).all()
    if github_user_aliases is None or len(github_user_aliases) == 0:
        mark = types.InlineKeyboardMarkup()
        mark.row(types.InlineKeyboardButton(User.back_inf,
                                            callback_data=" " + User.back_cal))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Список сохранённых alias пуст. "
                                   "Добавьте пользователя, чей репозиторий вы хотите выбрать.",
                              reply_markup=mark)

    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=User.user_history_aliases_ans,
                              reply_markup=user_opts.aliases_kb_for_user(call.message.chat.id, session))
    update_user_state_with_session(call.message.chat.id, States.S_ADD_REPOS, session)
    finish_session(session)


#  we pick add pr
def is_pr_add(data):
    return User.pr_add in data.split(' ')


@bot.callback_query_handler(func=lambda call: (
        is_pr_add(call.data)
        or (
                get_user_state(call.message.chat.id) == States.S_LOOK_REPO_PRS
                and call.data.split(" ")[-1] == user_opts.User.back_cal)
))
def query_handler(call):
    session = Session(db_engine)
    repos_aliases = session.query(GitHubRepos.tg_alias_repos).filter_by(
        tg_user_id=call.message.chat.id
    ).all()
    if repos_aliases is None or len(repos_aliases) == 0:
        mark = types.InlineKeyboardMarkup()
        mark.row(types.InlineKeyboardButton(User.back_inf,
                                            callback_data=" " + User.back_cal))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Список сохранённых alias пуст. "
                                   "Добавьте репозиторий, pull request которого вам интересен.",
                              reply_markup=mark)

    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=User.repos_history_aliases_ans,
                              reply_markup=user_opts.aliases_kb_for_repos(call.message.chat.id, session))
    update_user_state_with_session(call.message.chat.id, States.S_ADD_PR, session)
    finish_session(session)


# -------------------------------
# "back" when we looked alias from user history
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_LOOK_USER_ALI and
        call.data.split(" ")[-1] == ans.Answers.back_cal))
def query_handler(call):
    session = Session(db_engine)
    update_user_state_with_session(call.message.chat.id, States.S_CHOOSE_USER, session)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=User.user_history_aliases_ans,
                          reply_markup=user_opts.aliases_kb_for_user(call.message.chat.id, session))
    finish_session(session)


# "back" when we looked alias from repos history
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_LOOK_REPOS_ALI and
        call.data.split(" ")[-1] == ans.Answers.back_cal))
def query_handler(call):
    session = Session(db_engine)
    update_user_state_with_session(call.message.chat.id, States.S_CHOOSE_REPOS, session)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=User.repos_history_aliases_ans,
                          reply_markup=user_opts.aliases_kb_for_repos(call.message.chat.id, session))
    finish_session(session)


# "back" when we looked alias from pr history
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_LOOK_PR_ALI and
        call.data.split(" ")[-1] == ans.Answers.back_cal))
def query_handler(call):
    session = Session(db_engine)
    update_user_state_with_session(call.message.chat.id, States.S_CHOOSE_PR, session)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=User.pr_history_aliases_ans,
                          reply_markup=user_opts.aliases_kb_for_pr(call.message.chat.id, session))
    finish_session(session)


# ----------------------------------------------------------------------------------------------
#  pick back to main menu
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_LOOK_USER_ALI and
        call.data.split(" ")[-1] == ans.Answers.back_to_menu_cal))
def query_handler(call):
    update_user_state(call.message.chat.id, States.S_START)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=Answers.start_ans, reply_markup=ans.start_kb_for_all())


#  pick back to main menu
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_LOOK_REPOS_ALI and
        call.data.split(" ")[-1] == ans.Answers.back_to_menu_cal))
def query_handler(call):
    update_user_state(call.message.chat.id, States.S_START)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=Answers.start_ans, reply_markup=ans.start_kb_for_all())


#  pick back to main menu
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_LOOK_PR_ALI and
        call.data.split(" ")[-1] == ans.Answers.back_to_menu_cal))
def query_handler(call):
    update_user_state(call.message.chat.id, States.S_START)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=Answers.start_ans, reply_markup=ans.start_kb_for_all())


# ----------------------------------------------------------------------------------------------
#  we pick alias from our history list
def is_user_alias(data, call):
    print(data)
    print(User.user_alias_cal in data.split(' '))
    print(data.split(" ")[-1] != user_opts.User.back_cal)
    print(get_user_state(call.message.chat.id) == States.S_CHOOSE_USER)
    return User.user_alias_cal in data.split(' ')


@bot.callback_query_handler(func=lambda call: (
        is_user_alias(call.data, call)
        and (get_user_state(call.message.chat.id) == States.S_CHOOSE_USER
             or get_user_state(call.message.chat.id) == States.S_ALI_USER_ADDED)  # user control branch
        and call.data.split(" ")[-1] != user_opts.User.back_cal))
def query_handler(call):
    alias = ' '.join(call.data.split(" ")[:-1])
    user_id = call.message.chat.id

    session = Session(db_engine)
    github_user = session.query(GitHubUsers).filter_by(
        tg_user_id=user_id,
        tg_alias_user=alias
    ).first()

    name = github_user.gh_username
    url = github_user.hg_user_url
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="🔘 Имя: {}\n"
                               "🔘 Ссылка на пользователя: {}.".format(name, url),
                          reply_markup=ans.back_to_menu_and_back_kb())
    update_user_state_with_session(call.message.chat.id, States.S_LOOK_USER_ALI, session)
    finish_session(session)


@bot.callback_query_handler(func=lambda call: (
        (
                is_user_alias(call.data)
                and get_user_state(call.message.chat.id) == States.S_ADD_REPOS  # repos control stream
                and call.data.split(" ")[-1] != user_opts.User.back_cal)
        or (
                get_user_state(call.message.chat.id) == States.S_ALI_REPOS_ENTER
                and call.data.split(" ")[-1] == user_opts.User.back_cal))
                            )
def query_handler(call):
    session = Session(db_engine)
    if call.data.split(" ")[-1] == user_opts.User.back_cal:
        user_id = call.message.chat.id
        delete_null_alias_from_repos(user_id, session)

    alias = ' '.join(call.data.split(" ")[:-1])
    user_id = call.message.chat.id
    github_user = session.query(GitHubUsers).filter_by(
        tg_user_id=user_id,
        tg_alias_user=alias
    ).first()

    name = github_user.login
    query_url = f"https://api.github.com/users/{name}/repos"
    headers = {'Authorization': f'token {token}'}
    r = requests.get(query_url, headers=headers)
    if r.status_code == 200:
        dict_data = json.loads(r.text)

        if len(dict_data) != 0:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=User.repos_github_list,
                                  reply_markup=user_opts.gh_repos_list(dict_data))
        else:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="Список репозиториев выбранного пользователя пуст",
                                  reply_markup=ans.back_to_previous_kb())

    else:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Что-то пошло не так",
                              reply_markup=ans.back_to_previous_kb())

    update_user_state_with_session(call.message.chat.id, States.S_LOOK_USER_REPOS, session)
    finish_session(session)


#  we pick alias from our history list
def is_repos_alias(data):
    return User.repos_alias_cal in data.split(' ')


@bot.callback_query_handler(func=lambda call: (
        is_repos_alias(call.data)
        and (get_user_state(call.message.chat.id) == States.S_CHOOSE_REPOS
             or get_user_state(call.message.chat.id) == States.S_ALI_REPOS_ADDED)  # repos control stream
        and call.data.split(" ")[-1] != user_opts.User.back_cal))
def query_handler(call):
    alias = ' '.join(call.data.split(" ")[:-1])
    user_id = call.message.chat.id
    session = Session(db_engine)

    github_repos = session.query(GitHubRepos).filter_by(
        tg_user_id=user_id,
        tg_alias_repos=alias
    ).first()

    name = github_repos.gh_reposname
    url = github_repos.gh_repos_url
    description = github_repos.gh_repos_description
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="🔘 Репозиторий: {}\n"
                               "🔘 Ссылка на репозиторий: {}\n"
                               "🔘 Описание: {}.".format(name, url, description),
                          reply_markup=ans.back_to_menu_and_back_kb())
    update_user_state_with_session(call.message.chat.id, States.S_LOOK_REPOS_ALI, session)
    finish_session(session)


@bot.callback_query_handler(func=lambda call: (
        (
                is_repos_alias(call.data)
                and get_user_state(call.message.chat.id) == States.S_ADD_PR  # pr control stream
                and call.data.split(" ")[-1] != user_opts.User.back_cal)
        or (
                get_user_state(call.message.chat.id) == States.S_ALI_PR_ENTER
                and call.data.split(" ")[-1] == user_opts.User.back_cal))
                            )
def query_handler(call):
    session = Session(db_engine)
    if call.data.split(" ")[-1] == user_opts.User.back_cal:
        user_id = call.message.chat.id
        delete_null_alias_from_pull_requests(user_id, session)

    alias = ' '.join(call.data.split(" ")[:-1])
    user_id = call.message.chat.id

    github_repos = session.query(GitHubRepos).filter_by(
        tg_user_id=user_id,
        tg_alias_repos=alias
    ).first()

    name = github_repos.gh_reposname
    query_url = f"https://api.github.com/repos/{name}/pulls"
    headers = {'Authorization': f'token {token}'}
    r = requests.get(query_url, headers=headers)
    if r.status_code == 200:
        dict_data = json.loads(r.text)

        if len(dict_data) != 0:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=User.pr_github_list,
                                  reply_markup=user_opts.gh_pr_list(dict_data))
        else:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="Список pull request выбранного репозитория пуст",
                                  reply_markup=ans.back_to_previous_kb())

    else:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Что-то пошло не так",
                              reply_markup=ans.back_to_previous_kb())

    update_user_state_with_session(call.message.chat.id, States.S_LOOK_REPO_PRS, session)
    finish_session(session)


#  we pick alias from our history list
def is_pr_alias(data):
    return User.pr_alias_cal in data.split(' ')


@bot.callback_query_handler(func=lambda call: (
        is_pr_alias(call.data)
        and call.data.split(" ")[-1] != user_opts.User.back_cal))
def query_handler(call):
    alias = ' '.join(call.data.split(" ")[:-1])
    user_id = call.message.chat.id
    session = Session(db_engine)
    pull_request = session.query(GitHubPullRequest).filter_by(
        tg_user_id=user_id,
        tg_alias_pr=alias
    ).first()
    url = pull_request.gh_pr_url
    title = pull_request.gh_pr_title
    state = pull_request.gh_pr_state
    comments_num = pull_request.gh_commits
    changed_files = pull_request.gh_changed_files
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="🔘 Pull request: {}\n"
                               "🔘 Ссылка на pull request: {}\n"
                               "🔘 Статус: {}\n"
                               "🔘 Количество коммитов: {}\n"
                               "🔘 Количество измененных файлов: {}."
                          .format(title,
                                  url,
                                  state,
                                  comments_num,
                                  changed_files),
                          reply_markup=ans.back_to_menu_and_back_kb())
    update_user_state_with_session(call.message.chat.id, States.S_LOOK_PR_ALI, session)
    finish_session(session)


# END callback.handlers
# ---------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------
# START MESS HANDLERS
# "back" when we entered gh username
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_ALI_USER_ENTER and
        call.data.split(" ")[-1] == ans.Answers.back_cal))
def query_handler(call):
    user_id = call.message.chat.id
    session = Session(db_engine)
    delete_null_alias_from_users(user_id, session)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=ans.back_to_previous_kb(),
                          text="Введите имя пользователя:")
    update_user_state_with_session(call.message.chat.id, States.S_ADD_USER, session)
    finish_session(session)


# ---------------------------------------------------------------------------------------------
#  we entered user gitname
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == States.S_ADD_USER)
def user_adding(message):
    query_url = f"https://api.github.com/users/{message.text}"
    headers = {'Authorization': f'token {token}'}
    r = requests.get(query_url, headers=headers)
    if r.status_code == 200:
        dict_data = json.loads(r.text)
        name = dict_data['name'] if dict_data['name'] is not None else dict_data['login']

        # Trying to find such users in database
        session = Session(db_engine)
        github_user = session.query(GitHubUsers).filter_by(
            tg_user_id=message.from_user.id,
            gh_username=name
        ).first()
        if github_user is not None:
            # Such user has already been added to the database
            bot.send_message(chat_id=message.chat.id,
                             text="Такой пользователь уже существует в вашем сохранённом списке под псевдонимом: {}. "
                                  "Введите другой ник.".format(github_user.tg_alias_user),
                             reply_markup=ans.back_to_previous_kb())
        else:
            dict_data = json.loads(r.text)
            gh_username = dict_data['name'] if dict_data['name'] is not None else dict_data['login']
            github_user = GitHubUsers(tg_user_id=message.from_user.id,
                                      tg_alias_user=None,
                                      gh_user_url=dict_data['html_url'],
                                      gh_username=gh_username,
                                      gh_user_avatar=dict_data['avatar_url'],
                                      login=dict_data['login'])
            session.add(github_user)
            session.commit()
            update_user_state_with_session(message.from_user.id, States.S_ALI_USER_ENTER, session)
            bot.send_message(chat_id=message.chat.id,
                             reply_markup=ans.back_to_previous_kb(),
                             text=f"Введите alias для нового пользователя {dict_data['login']}.")
        finish_session(session)

    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Такого пользователя найти не удалось, попробуйте ввести ник правильно.",
                         reply_markup=ans.back_to_previous_kb())


def is_repos_from_gh(data):
    return User.repos_gh_cal in data.split(' ')


#  we entered repos gitname
@bot.callback_query_handler(func=lambda call: is_repos_from_gh(call.data))
def repos_adding(call):
    user_login = call.data.split('/')[0]
    session = Session(db_engine)
    github_user = session.query(GitHubUsers).filter_by(
        tg_user_id=call.from_user.id,
        login=user_login
    ).first()
    user_alias = github_user.tg_alias_user

    query_url = f"https://api.github.com/repos/{call.data.split()[0]}"
    headers = {'Authorization': f'token {token}'}
    r = requests.get(query_url, headers=headers)
    if r.status_code == 200:
        dict_data = json.loads(r.text)
        name = dict_data['full_name'] if dict_data['full_name'] is not None else dict_data['id']
        github_repos = session.query(GitHubRepos).filter_by(
            tg_user_id=call.from_user.id,
            gh_reposname=name
        ).first()

        if github_repos is not None:
            alias = github_repos.tg_alias_repos
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="Такой репозиторий уже существует в вашем сохранённом списке "
                                       "под псевдонимом: {}. "
                                       "Введите другой.".format(alias),
                                  reply_markup=ans.back_to_previous_kb(user_alias))
        else:
            dict_data = json.loads(r.text)
            gh_reposname = dict_data['full_name'] if dict_data['full_name'] is not None else dict_data['id']

            github_repos = GitHubRepos(tg_user_id=call.from_user.id,
                                       gh_reposname=gh_reposname,
                                       gh_repos_url=dict_data['html_url'],
                                       gh_repos_description=dict_data['description'])
            session.add(github_repos)
            session.commit()
            update_user_state_with_session(call.from_user.id, States.S_ALI_REPOS_ENTER, session)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=ans.back_to_previous_kb(user_alias),
                                  text=f"Введите alias для нового репозитория {gh_reposname}.")

    else:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Такой репозиторий найти не удалось, попробуйте ввести данные правильно.",
                              reply_markup=ans.back_to_previous_kb(user_alias))

    update_user_state_with_session(call.from_user.id, States.S_ALI_REPOS_ENTER, session)
    finish_session(session)


def is_pr_from_gh(data):
    return User.pr_gh_cal in data.split(' ')


#  we entered pr gitname
@bot.callback_query_handler(func=lambda call: is_pr_from_gh(call.data))
def pr_adding(call):
    tokens = call.data.split()[0].split('/')

    repos_fullname = f'{tokens[0]}/{tokens[1]}'

    session = Session(db_engine)
    github_repos = session.query(GitHubRepos).filter_by(
        tg_user_id=call.from_user.id,
        gh_reposname=repos_fullname
    ).first()
    repos_alias = github_repos.tg_alias_repos

    query_url = f"https://api.github.com/repos/{tokens[0]}/{tokens[1]}/pulls/{tokens[2]}"
    headers = {'Authorization': f'token {token}'}
    r = requests.get(query_url, headers=headers)
    if r.status_code == 200:
        dict_data = json.loads(r.text)
        name = dict_data['id']

        pull_request = session.query(GitHubPullRequest).filter_by(
            tg_user_id=call.from_user.id,
            gh_prid=name
        ).first()

        if pull_request is not None:
            alias = pull_request.tg_alias_pr
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="Такой pull request уже существует в вашем сохранённом списке "
                                       "под псевдонимом: {}. "
                                       "Выберите другой.".format(alias),
                                  reply_markup=ans.back_to_previous_kb(repos_alias))
        else:
            dict_data = json.loads(r.text)
            gh_prname = dict_data['id']

            pull_request = GitHubPullRequest(tg_user_id=call.from_user.id,
                                             gh_prname=gh_prname,
                                             gh_pr_url=dict_data['html_url'],
                                             gh_pr_title=dict_data['title'],
                                             gh_pr_state=dict_data['state'],
                                             gh_commits=dict_data['commits'],
                                             gh_changed_files=dict_data['changed_files'])
            session.add(pull_request)
            session.commit()
            update_user_state_with_session(call.from_user.id, States.S_ALI_PR_ENTER, session)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=ans.back_to_previous_kb(repos_alias),
                                  text=f"Введите alias для нового pull request {call.data.split()[0]}.")

    else:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Такой pull request найти не удалось, попробуйте ввести данные правильно.",
                              reply_markup=ans.back_to_previous_kb(repos_alias))

    update_user_state_with_session(call.from_user.id, States.S_ALI_PR_ENTER, session)
    finish_session(session)


# ---------------------------------------------------------------------------------------------
#  pick back to main menu
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_ALI_USER_ADDED and
        call.data.split(" ")[-1] == ans.Answers.back_to_menu_cal))
def query_handler(call):
    update_user_state(call.message.chat.id, States.S_START)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=Answers.start_ans, reply_markup=ans.start_kb_for_all())


#  pick back to main menu
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_ALI_REPOS_ADDED and
        call.data.split(" ")[-1] == ans.Answers.back_to_menu_cal))
def query_handler(call):
    update_user_state(call.message.chat.id, States.S_START)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=Answers.start_ans, reply_markup=ans.start_kb_for_all())


#  pick back to main menu
@bot.callback_query_handler(func=lambda call: (
        get_user_state(call.message.chat.id) == States.S_ALI_PR_ADDED and
        call.data.split(" ")[-1] == ans.Answers.back_to_menu_cal))
def query_handler(call):
    update_user_state(call.message.chat.id, States.S_START)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=Answers.start_ans, reply_markup=ans.start_kb_for_all())


# ---------------------------------------------------------------------------------------------
def is_user_ali_added(data):
    return ans.Answers.ali_user_added_cal in data.split(' ')


#  (added new alias) we enter give me info about user
@bot.callback_query_handler(func=lambda call: is_user_ali_added(call.data))
def query_handler(call):
    user_id = call.message.chat.id
    alias = ' '.join(call.data.split(' ')[:-1])

    session = Session(db_engine)
    github_user = session.query(GitHubUsers).filter_by(
        tg_user_id=user_id,
        tg_alias_user=alias
    ).first()

    name = github_user.gh_username
    url = github_user.gh_user_url
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="🔘 Имя: {}\n"
                               "🔘 Ссылка на пользователя: {}.".format(name, url),
                          reply_markup=ans.back_to_menu_kb())
    finish_session(session)


def is_repos_ali_added(data):
    return ans.Answers.ali_repos_added_cal in data.split(' ')


#  (added new alias) we enter give me info about repos
@bot.callback_query_handler(func=lambda call: is_repos_ali_added(call.data))
def query_handler(call):
    user_id = call.message.chat.id
    alias = ' '.join(call.data.split(' ')[:-1])

    session = Session(db_engine)
    github_repos = session.query(GitHubRepos).filter_by(
        tg_user_id=user_id,
        tg_alias_repos=alias
    ).first()

    name = github_repos.gh_reposname
    url = github_repos.gh_repos_url
    description = github_repos.gh_repos_description
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="🔘 Репозиторий: {}\n"
                               "🔘 Ссылка на репозиторий: {}\n"
                               "🔘 Описание: {}.".format(name, url, description),
                          reply_markup=ans.back_to_menu_kb())
    finish_session(session)


def is_pr_ali_added(data):
    return ans.Answers.ali_pr_added_cal in data.split(' ')


#  (added new alias) we enter give me info about pr
@bot.callback_query_handler(func=lambda call: is_pr_ali_added(call.data))
def query_handler(call):
    user_id = call.message.chat.id
    alias = ' '.join(call.data.split(' ')[:-1])

    session = Session(db_engine)
    pull_request = session.query(GitHubPullRequest).filter_by(
        tg_user_id=user_id,
        tg_alias_pr=alias
    ).first()

    url = pull_request.gh_pr_url
    title = pull_request.gh_pr_title
    state = pull_request.gh_pr_state
    commits_num = pull_request.gh_commits
    changed_files = pull_request.gh_changed_files
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="🔘 Pull request: {}\n"
                               "🔘 Ссылка на pull request: {}\n"
                               "🔘 Статус: {}\n"
                               "🔘 Количество коммитов: {}\n"
                               "🔘 Количество измененных файлов: {}."
                          .format(title,
                                  url,
                                  state,
                                  commits_num,
                                  changed_files),
                          reply_markup=ans.back_to_menu_kb())
    finish_session(session)


# ---------------------------------------------------------------------------------------------
#  we enter alias for user
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == States.S_ALI_USER_ENTER)
def alias_adding(message):
    user_id = message.from_user.id
    alias = ' '.join(message.text.split())

    session = Session(db_engine)
    github_user = session.query(GitHubUsers).filter_by(
        tg_user_id=user_id,
        tg_alias_user=alias
    ).first()
    if github_user is None:
        github_user = session.query(GitHubUsers).filter_by(
            tg_user_id=user_id,
            tg_alias_user=None  # noqa
        ).first()
        github_user.tg_alias_user = alias
        session.commit()
        update_user_state_with_session(message.from_user.id, States.S_ALI_USER_ADDED, session)
        bot.send_message(chat_id=message.chat.id, reply_markup=ans.user_ali_added_kb(alias),
                         text="Пользователь {} добавлен.".format(alias))
    else:
        bot.send_message(chat_id=message.chat.id, reply_markup=ans.back_to_previous_kb(),
                         text="Такой alias уже есть. Введите уникальный.")
    finish_session(session)


#  we enter alias for repos
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == States.S_ALI_REPOS_ENTER)
def alias_adding(message):
    user_id = message.from_user.id
    alias = ' '.join(message.text.split())

    session = Session(db_engine)
    github_repos = session.query(GitHubRepos).filter_by(
        tg_user_id=user_id,
        tg_alias_repos=alias
    ).first()

    if github_repos is None:
        github_repos = session.query(GitHubRepos).filter_by(
            tg_user_id=user_id,
            tg_alias_repos=None  # noqa
        ).first()
        github_repos.tg_alias_repos = alias
        session.commit()
        update_user_state_with_session(message.from_user.id, States.S_ALI_REPOS_ADDED, session)
        bot.send_message(chat_id=message.chat.id, reply_markup=ans.repos_ali_added_kb(alias),
                         text="Репозиторий {} добавлен.".format(alias))
    else:
        login = github_repos.gh_reposname.split('/')[0]
        github_user_alias = session.query(GitHubUsers.tg_alias_user).filter_by(
            tg_user_id=user_id,
            login=login
        ).first()

        bot.send_message(chat_id=message.chat.id, reply_markup=ans.back_to_previous_kb(github_user_alias),
                         text="Такой alias уже есть. Введите уникальный.")
    finish_session(session)


#  we enter alias for pr
@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == States.S_ALI_PR_ENTER)
def alias_adding(message):
    user_id = message.from_user.id
    alias = ' '.join(message.text.split())

    session = Session(db_engine)
    pull_request = session.query(GitHubPullRequest).filter_by(
        tg_user_id=user_id,
        tg_alias_pr=alias
    ).first()

    if pull_request is None:
        pull_request = session.query(GitHubPullRequest).filter_by(
            tg_user_id=user_id,
            tg_alias_pr=None  # noqa
        ).first()
        pull_request.tg_alias_pr = alias
        session.commit()
        update_user_state_with_session(message.from_user.id, States.S_ALI_PR_ADDED, session)
        bot.send_message(chat_id=message.chat.id, reply_markup=ans.pr_ali_added_kb(alias),
                         text="Pull request {} добавлен.".format(alias))
    else:
        gh_pr_url = pull_request.gh_pr_url
        repo = '/'.join(gh_pr_url.split('/')[-4:-2])

        repos_alias = session.query(GitHubRepos.tg_alias_repos).filter_by(
            tg_user_id=user_id,
            gh_reposname=repo
        ).first()

        bot.send_message(chat_id=message.chat.id, reply_markup=ans.back_to_previous_kb(repos_alias),
                         text="Такой alias уже есть. Введите уникальный.")
    finish_session(session)


# END MESS HANDLERS
# ---------------------------------------------------------------------------------------------


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
