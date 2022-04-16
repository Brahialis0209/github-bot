from enum import Enum

from telebot import types



class States(Enum):
    S_START = 0  # Dialog start
    S_USER_CONTROL = 1  # user pick user's control
    S_CHOOSE_USER = 2  # choose usr from db
    S_ADD_USER = 3  # add new usr



# template of callback data: "[name-of-topic].[section].[page-number]"
def start_kb_for_user():
    start_page = 0
    sect_1_button = types.InlineKeyboardButton(User.choose,
                                               callback_data=User.user_choice + " " + str(start_page))
    sect_2_button = types.InlineKeyboardButton(User.new,
                                               callback_data=User.user_add + " " + str(start_page))
    math_mark = types.InlineKeyboardMarkup(row_width=1)
    math_mark.add(sect_1_button, sect_2_button)
    return math_mark


class User:
    ans = "Выберите что вы хотите сделать"
    choose = "Выбрать из истории"
    new = "Добавить нового"

    user_add = "user_add"
    user_choice = "user_choice"
    user_url = "user_url"