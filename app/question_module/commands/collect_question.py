# -*- coding: utf-8 -*-

import json
import time
import dougrain
from flask.ext.script import Command, Option
from app.question_module.exceptions.request_exceptions import WrongStatusCodeException, NoContentException
from pip.backwardcompat import raw_input
import requests


class CollectQuestion(Command):
    """Collects the latest question on the question server"""

    url_format = "http://%s/%s"

    option_list = (
        Option("-h", "--host", help="Question server address", required=True),
        Option("-u", "--url", help="Path to the question", required=True),
        Option("-t", "--time", help="Time to wait before requesting the next question"),
    )

    def run(self, host, url, time=5000):
        while True:
            print("Connecting to server...")
            question = self.request_question(host, url)

            if question is not None:
                answer = raw_input(question.properties["question"])
                self.post_answer(host, question.links["answer"].url(), answer)
                print("Answer submitted...")
            else:
                print("No question to answer...")
                print("Going to sleep for %d ms..." % time)
                time.sleep(time)

    def request_question(self, host, url):
        response = requests.get(self.url_format % (host, url))

        if response.status_code == 204:
            return None
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
