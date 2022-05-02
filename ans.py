from telebot import types


def start_kb_for_all():
    sect_1_button = types.InlineKeyboardButton(Answers.user_inf,
                                               callback_data=Answers.user_control + " " + str(Answers.user_page))
    sect_2_button = types.InlineKeyboardButton(Answers.repo_inf,
                                               callback_data=Answers.repos_control + " " + str(Answers.repo_page))
    sect_3_button = types.InlineKeyboardButton(Answers.pr_inf,
                                               callback_data=Answers.pr_control + " " + str(Answers.pr_page))
    start_mark = types.InlineKeyboardMarkup()
    start_mark.row(sect_1_button)
    start_mark.row(sect_2_button)
    start_mark.row(sect_3_button)
    return start_mark


def user_ali_added_kb(alias):
    button_1 = types.InlineKeyboardButton(Answers.ali_user_added_inf,
                                          callback_data=Answers.ali_user_added_cal + " " + str(alias))
    button_3 = types.InlineKeyboardButton(Answers.back_to_menu_inf,
                                          callback_data=" " + Answers.back_to_menu_cal)
    # button_2 = types.InlineKeyboardButton(Answers.back_inf,
    #                                       callback_data=" " + Answers.back_cal)
    mark = types.InlineKeyboardMarkup(row_width=1)
    mark.add(button_1, button_3)
    return mark


def repos_ali_added_kb(alias):
    button_1 = types.InlineKeyboardButton(Answers.ali_repos_added_inf,
                                          callback_data=Answers.ali_repos_added_cal + " " + str(alias))
    button_3 = types.InlineKeyboardButton(Answers.back_to_menu_inf,
                                          callback_data=" " + Answers.back_to_menu_cal)
    # button_2 = types.InlineKeyboardButton(Answers.back_inf,
    #                                       callback_data=" " + Answers.back_cal)
    mark = types.InlineKeyboardMarkup(row_width=1)
    mark.add(button_1, button_3)
    return mark


def back_to_menu_kb():
    button_2 = types.InlineKeyboardButton(Answers.back_to_menu_inf,
                                          callback_data=" " + Answers.back_to_menu_cal)
    mark = types.InlineKeyboardMarkup(row_width=1)
    mark.add(button_2)
    return mark


def back_to_menu_and_back_kb():
    button_1 = types.InlineKeyboardButton(Answers.back_inf,
                                          callback_data=" " + Answers.back_cal)
    button_2 = types.InlineKeyboardButton(Answers.back_to_menu_inf,
                                          callback_data=" " + Answers.back_to_menu_cal)
    mark = types.InlineKeyboardMarkup(row_width=1)
    mark.add(button_1, button_2)
    return mark


def back_to_previous_kb():
    button = types.InlineKeyboardButton(Answers.back_inf,
                                        callback_data=" " + Answers.back_cal)
    mark = types.InlineKeyboardMarkup(row_width=1)
    mark.add(button)
    return mark


class Answers:
    greeting_old = "Давай продолжим общение. Кажется мы остановились тут. \n "

    ali_user_added_inf = "Вывести информацию о пользователе"
    ali_repos_added_inf = "Вывести информацию о репозитории"

    ali_user_added_cal = "ali_user_added_cal"
    ali_repos_added_cal = "ali_repos_added_cal"

    back_to_menu_cal = "back_to_menu_cal"
    back_inf = "Назад"
    back_cal = "back_cal"

    user_page = 1
    repo_page = 2
    pr_page = 3
    start_markup = types.ReplyKeyboardMarkup()
    start_inf = "Старт"
    back_to_menu_inf = "Вернуться в главное меню"
    repo_inf = "Получить информацию о репозитории (В разработке)"
    user_inf = "Получить информацию о пользователе"
    pr_inf = "Получить информацию о pull request(В разработке)"
    start_markup.row(user_inf)
    start_markup.row(repo_inf)
    start_markup.row(pr_inf)

    back = "Назад"

    start_ans = "Приветствую. Бот позволяет найти информацию о пользователях, репозиториях и пулл-реквестах GitHub."

    reference_ans = "Шаблон(скоро добавить)"

    user_control = "user_control"
    pr_control = "pr_control"
    repos_control = "repo_control"
