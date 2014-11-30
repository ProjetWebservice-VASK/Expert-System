from flask.ext.script import Command
from app.question_module.exceptions.request_exceptions import WrongStatusCodeException, NoContentException
import requests


class CollectQuestion(Command):
    """Collects the latest question on the question server"""

    def run(self):
        print("Connecting to server...")
        question = self.request_question()
        print(question)

    def request_question(self):
        response = requests.get("server-name.com/question/pending/latest")

        if response.status_code == 204:
            raise NoContentException()
        elif response.status_code != 200:
            raise WrongStatusCodeException(response.status_code)

        return response.content
