from telebot import types
from sqlalchemy import select
from sqlalchemy.orm import Session
from data_models import GitHubUsers, GitHubRepos, GitHubPullRequest


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
    S_REPOS_CONTROL = 11  # user pick repo's control
    S_CHOOSE_REPOS = 12  # choose repos from db
    S_LOOK_REPOS_ALI = 13  # look alias from history
    S_ADD_REPOS = 14  # add new repos
    S_LOOK_USER_REPOS = 15  # look user's repos
    S_ALI_REPOS_ENTER = 16  # add repos alias
    S_ALI_REPOS_ADDED = 17  # added repos alias

    # pr info
    S_PR_CONTROL = 21  # user pick user's control
    S_CHOOSE_PR = 22  # choose usr from db
    S_LOOK_PR_ALI = 23  # look alias from history
    S_ADD_PR = 24  # add new usr
    S_LOOK_REPO_PRS = 25  # look user's repos
    S_ALI_PR_ENTER = 26  # add user alias
    S_ALI_PR_ADDED = 27  # added user alias


def aliases_kb_for_user(user_id, session: Session):
    # Empty aliases list is not allowed here
    aliases = session.query(GitHubUsers.tg_alias_user).filter_by(tg_user_id=user_id).all()
    mark = types.InlineKeyboardMarkup()
    for alias in aliases:
        alias_str = str(alias[0])
        mark.row(types.InlineKeyboardButton(alias_str,
                                            callback_data=alias_str + " " + User.user_alias_cal))
    mark.row(types.InlineKeyboardButton(User.back_inf,
                                        callback_data=" " + User.back_cal))
    return mark


def aliases_kb_for_repos(user_id, session: Session):
    # Empty aliases list is not allowed here
    aliases = session.query(GitHubRepos.tg_alias_repos).filter_by(tg_user_id=user_id).all()
    mark = types.InlineKeyboardMarkup()
    for alias in aliases:
        alias_str = str(alias[0])
        mark.row(types.InlineKeyboardButton(alias_str,
                                            callback_data=alias_str + " " + User.repos_alias_cal))
    mark.row(types.InlineKeyboardButton(User.back_inf,
                                        callback_data=" " + User.back_cal))
    return mark


def aliases_kb_for_pr(user_id, session: Session):
    # Empty aliases list is not allowed here
    aliases = session.query(GitHubPullRequest.tg_alias_pr).filter_by(tg_user_id=user_id).all()
    mark = types.InlineKeyboardMarkup()
    for alias in aliases:
        alias_str = str(alias[0])
        mark.row(types.InlineKeyboardButton(alias_str,
                                            callback_data=alias_str + " " + User.pr_alias_cal))
    mark.row(types.InlineKeyboardButton(User.back_inf,
                                        callback_data=" " + User.back_cal))
    return mark


def gh_repos_list(data):
    mark = types.InlineKeyboardMarkup()
    for repos in data:
        mark.row(types.InlineKeyboardButton(repos['name'],
                                            callback_data=repos['full_name'] + " " + User.repos_gh_cal))
    mark.row(types.InlineKeyboardButton(User.back_inf,
                                        callback_data=" " + User.back_cal))
    return mark


def gh_pr_list(data):
    mark = types.InlineKeyboardMarkup()
    for repos in data:
        number = repos['number']
        repo = '/'.join(repos['html_url'].split('/')[-4:-2])
        title = f"#{number}: {repos['title']}"
        mark.row(types.InlineKeyboardButton(title,
                                            callback_data=f'{repo}/{number}' + " " + User.pr_gh_cal))
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


def start_kb_for_pr():
    button_1 = types.InlineKeyboardButton(User.choose,
                                          callback_data=User.pr_choice)
    button_2 = types.InlineKeyboardButton(User.user_new,
                                          callback_data=User.pr_add)
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

    repos_gh_cal = "repos_gh_cal"
    pr_gh_cal = "pr_gh_cal"

    ans = "Выберите что вы хотите сделать"
    user_history_aliases_ans = "Выберите сохранённого пользователя чтобы получить информацию"
    repos_history_aliases_ans = "Выберите сохранённый репозиторий чтобы получить информацию"
    pr_history_aliases_ans = "Выберите сохранённый pull request чтобы получить информацию"
    repos_github_list = "Выберите репозиторий"
    pr_github_list = "Выберите pull request"
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
