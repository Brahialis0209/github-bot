from telebot import types



class Answers:
    main_markup = types.ReplyKeyboardMarkup()
    repo_inf = "Получить информацию о репозитории. (В разработке)"
    user_inf = "Получить информацию о пользователе."
    pr_inf = "Получить информацию о pull request.(В разработке)"
    main_markup.row(user_inf)
    main_markup.row(repo_inf)
    main_markup.row(pr_inf)

    back = "Назад"

    start_ans = "Приветствую. Бот позволяет найти информацию о пользователях, репозиториях и пулл-реквестах GitHub."

    reference_ans = "Шаблон(скоро добавить)"

    url_donate_path = 'https://money.yandex.ru/to/4100111962148422'
    url_team_leader = 'https://t.me/dont_open'
    url_bit_coin = 'https://topcash.me/ru/yamrub_to_btc'
    bit_coin_bill = 'bc1qwz2rcelzqdwh8y4kqupk3q5qrtsayltvnf955c'
