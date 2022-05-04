from telebot import types


class States:
    S_START = 0  # Dialog start

    # user info
    S_USER_CONTROL = 1  # user pick user's control
    S_CHOOSE_USER = 2  # choose usr from db
    S_LOOK_USER_ALI = 3  # look alias from history
    S_ADD_USER = 4  # add new usr
    S_ALI_USER_ENTER = 5  # add user alias
    S_ALI_USER_ADDED = 6  # added user alias

    # repos info
    S_REPOS_CONTROL = 7  # user pick user's control
    S_CHOOSE_REPOS = 8  # choose usr from db
    S_LOOK_REPOS_ALI = 9  # look alias from history
    S_ADD_REPOS = 10  # add new usr
    S_ALI_REPOS_ENTER = 11  # add user alias
    S_ALI_REPOS_ADDED = 12  # added user alias

    # pr info
    S_PR_CONTROL = 13  # user pick user's control
    S_CHOOSE_PR = 14  # choose usr from db
    S_LOOK_PR_ALI = 15  # look alias from history
    S_ADD_PR = 16  # add new usr
    S_ALI_PR_ENTER = 17  # add user alias
    S_ALI_PR_ADDED = 18  # added user alias


def aliases_kb_for_user(db_object, user_id):
    db_object.execute(
        f"SELECT tg_alias_user FROM gh_users WHERE tg_user_id = '{user_id}'")
    result = db_object.fetchall()
    len_hist = len(result)
    mark = types.InlineKeyboardMarkup()
    for i in range(len_hist):
        mark.row(types.InlineKeyboardButton(str(result[i][0]).replace(" ", ""),
                                            callback_data=str(result[i][0]).replace(" ",
                                                                                    "") + " " + User.user_alias_cal))
    mark.row(types.InlineKeyboardButton(User.back_inf,
                                        callback_data=" " + User.back_cal))
    return mark


def aliases_kb_for_repos(db_object, user_id):
    db_object.execute(
        f"SELECT tg_alias_repos FROM repos WHERE tg_user_id = '{user_id}'")
    result = db_object.fetchall()
    len_hist = len(result)
    mark = types.InlineKeyboardMarkup()
    for i in range(len_hist):
        mark.row(types.InlineKeyboardButton(str(result[i][0]).replace(" ", ""),
                                            callback_data=str(result[i][0]).replace(" ",
                                                                                    "") + " " + User.repos_alias_cal))
    mark.row(types.InlineKeyboardButton(User.back_inf,
                                        callback_data=" " + User.back_cal))
    return mark


def start_kb_for_user():
    button_1 = types.InlineKeyboardButton(User.choose,
                                          callback_data=User.user_choice)
    button_2 = types.InlineKeyboardButton(User.user_new,
                                          callback_data=User.user_add)
    button_3 = types.InlineKeyboardButton(User.back_inf,
                                          callback_data=" " + User.back_cal)
    mark = types.InlineKeyboardMarkup(row_width=1)
    mark.add(button_1, button_2, button_3)
    return mark


def start_kb_for_repos():
    button_1 = types.InlineKeyboardButton(User.choose,
                                          callback_data=User.repos_choice)
    button_2 = types.InlineKeyboardButton(User.user_new,
                                          callback_data=User.repos_add)
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

    user_alias_cal = "user_alias_cal"
    repos_alias_cal = "repos_alias_cal"
    pr_alias_cal = "pr_alias_cal"

    ans = "Выберите что вы хотите сделать"
    user_history_aliases_ans = "Выберите сохранённого пользователя чтобы получить информацию"
    repos_history_aliases_ans = "Выберите сохранённый репозиторий чтобы получить информацию"
    pr_history_aliases_ans = "Выберите сохранённый pull request чтобы получить информацию"
    choose = "Выбрать из истории"
    user_new = "Добавить нового"
    repos_new = "Добавить новый"
    pr_new = "Добавить новый"

    user_add = "user_add"
    user_choice = "user_choice"
    user_url = "user_url"

    repos_add = "repos_add"
    repos_choice = "repos_choice"
    repos_url = "repos_url"

    pr_add = "pr_add"
    pr_choice = "pr_choice"
    pr_url = "pr_url"
