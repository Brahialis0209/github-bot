from data_models import *  # noqa
from sqlalchemy.orm import Session


class DataBaseAccessor:
    @staticmethod
    def get_gh_user(tg_user_id, alias, session: Session):
        return session.query(GitHubUsers).filter_by(
            tg_user_id=tg_user_id,
            tg_alias_user=alias,
        ).first()

    @staticmethod
    def get_repos(tg_user_id, alias, session: Session):
        return session.query(GitHubRepos).filter_by(
            tg_user_id=tg_user_id,
            tg_alias_repos=alias,
        ).first()

    @staticmethod
    def get_pull(tg_user_id, alias, session: Session):
        return session.query(GitHubPullRequest).filter_by(
            tg_user_id=tg_user_id,
            tg_alias_pr=alias,
        ).first()
