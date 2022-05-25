import requests
import json


class DetailInfo:
    """
    Helper class to request detailed info about users, reposes and so on.
    Examples of details info: user avatar, pull request status
    """
    __status_code_success = 200

    @staticmethod
    def __repos_url_to_query(url):
        """
        url example: https://github.com/octocat/Hello-World
        we need: https://api.github.com/repos/octocat/Hello-World
        """
        return url.replace('//github.com/', '//api.github.com/repos/')

    @staticmethod
    def request_repos_details(token, repos_url):
        query_url = DetailInfo.__repos_url_to_query(repos_url)
        headers = {'Authorization': f'token {token}'}
        response = requests.get(query_url, headers=headers)
        if response.status_code == DetailInfo.__status_code_success:
            response_contents = json.loads(response.text)
            return {
                "description": response_contents['description'],
            }
        else:  # request failed
            raise RuntimeError(f"Request {query_url} (detailed info about repository) failed")

    @staticmethod
    def __pr_url_to_query(url):
        """
        url example: https://github.com/octocat/Hello-World/pull/1347
        we need: https://api.github.com/repos/octocat/Hello-World/pulls/1347
        """
        return url.replace("//github.com/", "//api.github.com/repos/").replace(
            '/pull/',
            '/pulls/'
        )


    @staticmethod
    def request_pull_details(token, url):
        query_url = DetailInfo.__pr_url_to_query(url)
        headers = {'Authorization': f'token {token}'}
        response = requests.get(query_url, headers=headers)
        if response.status_code == DetailInfo.__status_code_success:
            response_contents = json.loads(response.text)
            return {
                "title": response_contents["title"],
                "state": response_contents["state"],
                "commits": response_contents["commits"],
                "changed_files": response_contents["changed_files"],
            }
        else:  # request failed
            raise RuntimeError(f"Request {query_url} (detailed info about pull request) failed")
