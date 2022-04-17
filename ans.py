from telebot import types


def start_kb_for_all():
    start_page = 0
    sect_1_button = types.InlineKeyboardButton(Answers.user_inf,
                                               callback_data=Answers.user_inf + " " + str(start_page))
    sect_2_button = types.InlineKeyboardButton(Answers.repo_inf,
                                               callback_data=Answers.repo_inf + " " + str(start_page))
    sect_3_button = types.InlineKeyboardButton(Answers.pr_inf,
                                               callback_data=Answers.pr_inf + " " + str(start_page))
    start_mark = types.InlineKeyboardMarkup(row_width=1)
    start_mark.add(sect_1_button, sect_2_button, sect_3_button)
    return start_mark


class Answers:
    start_markup = types.ReplyKeyboardMarkup()
    start_inf = "Старт"
    start_markup.row(start_inf)
    repo_inf = "Получить информацию о репозитории. (В разработке)"
    user_inf = "Получить информацию о пользователе."
    pr_inf = "Получить информацию о pull request.(В разработке)"
    start_markup.row(user_inf)
    start_markup.row(repo_inf)
    start_markup.row(pr_inf)

    back = "Назад"

    start_ans = "Приветствую. Бот позволяет найти информацию о пользователях, репозиториях и пулл-реквестах GitHub."

    reference_ans = "Шаблон(скоро добавить)"

    url_donate_path = 'https://money.yandex.ru/to/4100111962148422'
    url_team_leader = 'https://t.me/dont_open'
    url_bit_coin = 'https://topcash.me/ru/yamrub_to_btc'
    bit_coin_bill = 'bc1qwz2rcelzqdwh8y4kqupk3q5qrtsayltvnf955c'
