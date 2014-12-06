# -*- coding: utf-8 -*-

import json
import dougrain
from flask.ext.script import Command, Option
from app.question_module.exceptions.request_exceptions import WrongStatusCodeException, NoContentException
from pip.backwardcompat import raw_input
import requests


class CollectQuestion(Command):
    """Collects the latest question on the question server"""

    url_format = "http://%s/%s"

    option_list = (
        Option('-h', '--host', help='Question server address'),
        Option('-u', '--url', help='Path to the question'),
    )

    def run(self, host, url):
        print("Connecting to server...")
        question = self.request_question(host, url)
        answer = raw_input(question.properties["question"])
        self.post_answer(host, question.links["answer"].url(), answer)
        print("Answer submitted...")

    def request_question(self, host, url):
        response = requests.get(self.url_format % (host, url))

        if response.status_code == 204:
            raise NoContentException()
        elif response.status_code != 200:
            raise WrongStatusCodeException(response)

        return dougrain.Document.from_object(response.json())

    def post_answer(self, host, answer_url, answer_text):
        answer_request = self.create_answer_request(host, answer_url, answer_text)
        response = requests.Session().send(answer_request.prepare())

        if response.status_code == 204:
            return True
        else:
            raise WrongStatusCodeException(response)

    def create_answer_request(self, host, answer_url, answer_text):
        request = requests.Request("PUT", self.url_format % (host, answer_url))

        if answer_text is not None:
            answer = {
                "answer": answer_text
            }
            request.json = answer

        return request
