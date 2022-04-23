from telebot import types



class States:
    S_START = 0  # Dialog start
    S_USER_CONTROL = 1  # user pick user's control
    S_CHOOSE_USER = 2  # choose usr from db
    S_LOOK_ALI = 3  # look alias from history
    S_ADD_USER = 4  # add new usr
    S_ALI_USER_ENTER = 5  # add user alias
    S_ALI_USER_ADDED = 6  # added user alias


def aliases_kb_for_user(db_object, user_id):
    db_object.execute(
        f"SELECT tg_alias_user FROM gh_users WHERE tg_user_id = '{user_id}'")
    result = db_object.fetchall()
    len_hist = len(result)
    mark = types.InlineKeyboardMarkup()
    for i in range(len_hist):
        mark.row(types.InlineKeyboardButton(str(result[i][0]).replace(" ", ""),
                                               callback_data=str(result[i][0]).replace(" ", "") + " " + User.alias_cal))
    mark.row(types.InlineKeyboardButton(User.back_inf,
                                        callback_data=" " + User.back_cal))
    return mark



def start_kb_for_user():
    button_1 = types.InlineKeyboardButton(User.choose,
                                               callback_data=User.user_choice + " " + str(User.user_add))
    button_2 = types.InlineKeyboardButton(User.new,
                                               callback_data=User.user_add + " " + str(User.user_choose))
    button_3 = types.InlineKeyboardButton(User.back_inf,
                                        callback_data=" " + User.back_cal)
    mark = types.InlineKeyboardMarkup(row_width=1)
    mark.add(button_1, button_2, button_3)
    return mark



class User:
    prev_list = "prev_list"
    next_list = "next_list"
    back_cal = "back_cal"
    back_inf = "Назад"

    alias_cal = "alias_cal"

    user_add = 5
    user_choose = 6
    ans = "Выберите что вы хотите сделать"
    choose = "Выбрать из истории"
    new = "Добавить нового"

    user_add = "user_add"
    user_choice = "user_choice"
    user_url = "user_url"