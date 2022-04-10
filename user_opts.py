from telebot import types


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