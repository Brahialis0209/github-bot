from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class TgUser(Base):
    __tablename__ = 'tg_users'

    tg_user_id = Column(Integer, primary_key=True)
    tg_username = Column(String)
    user_state = Column(Integer)  # Current state in UI

    # Relations (one to many)
    github_users = relationship("GitHubUsers", back_populates="tg_user")
    github_repos = relationship("GitHubRepos", back_populates="tg_user")
    github_pull_request = relationship("GitHubPullRequest", back_populates="tg_user")

    def __repr__(self):
        return f"TgUser(tg_user_id={self.tg_user_id!r}, \
        tg_username={self.tg_username!r}, user_state={self.user_state!r})"


class GitHubUsers(Base):
    __tablename__ = 'gh_users'

    row_id = Column(Integer, primary_key=True)
    tg_user_id = Column(Integer, ForeignKey('tg_users.tg_user_id'))
    tg_alias_user = Column(String)  # User-defined alias
    gh_user_url = Column(String)  # URL to request info about user
    login = Column(String)  # User login, needed to form URL for GitHub API
    # TODO: do not hold fields below in data base,
    #   get them with GitHub API by demand
    gh_username = Column(String)
    gh_user_avatar = Column(String)

    # Relation
    tg_user = relationship("TgUser", back_populates="github_users")


class GitHubRepos(Base):
    __tablename__ = 'repos'

    row_id = Column(Integer, primary_key=True)
    tg_user_id = Column(Integer, ForeignKey('tg_users.tg_user_id'))
    tg_alias_repos = Column(String)  # User-defined alias
    gh_repos_url = Column(String)  # URL to request info about repository
    # TODO: do not hold fields below in data base,
    #   get them with GitHub API by demand
    gh_reposname = Column(String)
    gh_repos_description = Column(String)

    # Relation
    tg_user = relationship("TgUser", back_populates="github_repos")


class GitHubPullRequest(Base):
    __tablename__ = 'pulls'

    row_id = Column(Integer, primary_key=True)
    tg_user_id = Column(Integer, ForeignKey('tg_users.tg_user_id'))
    tg_alias_pr = Column(String)  # User-defined alias
    gh_pr_url = Column(String)  # URL to request info about repository
    # TODO: do not hold fields below in data base,
    #   get them with GitHub API by demand
    gh_prid = Column(String)
    gh_pr_title = Column(String)
    gh_pr_state = Column(String)
    gh_commits = Column(String)
    gh_changed_files = Column(String)

    # Relation
    tg_user = relationship("TgUser", back_populates="github_pull_request")
