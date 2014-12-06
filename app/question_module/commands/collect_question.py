from flask.ext.script import Command, Option
from app.question_module.exceptions.request_exceptions import WrongStatusCodeException, NoContentException
from pip.backwardcompat import raw_input
import requests


class CollectQuestion(Command):
    """Collects the latest question on the question server"""

    option_list = (
        Option('-h', '--host', help='Question server address'),
        Option('-u', '--url', help='Path to the question'),
    )

    def run(self, host, url):
        print("Connecting to server...")
        question = self.request_question(host, url)
        answer = raw_input(question)

    @staticmethod
    def request_question(host, url):
        response = requests.get(host + "/" + url)

        if response.status_code == 204:
            raise NoContentException()
        elif response.status_code != 200:
            raise WrongStatusCodeException(response.status_code)

        return response.content
