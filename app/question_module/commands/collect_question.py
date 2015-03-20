# -*- coding: utf-8 -*-
import time

import dougrain
import random
from flask.ext.script import Command, Option
from app.question_module.exceptions.request_exceptions import WrongStatusCodeException, InvalidQuestionFormatException
import requests
from simplejson import JSONDecodeError


class CollectQuestion(Command):
    """Collects the latest question on the question server"""

    url_format = "http://%s/%s"

    option_list = (
        Option("-h", "--host", help="Question server address", required=True),
        Option("-u", "--url", help="Path to the question", required=True),
        Option("-t", "--timeout", help="Time to wait before requesting the next question", default=5000),
        Option("-a", "--auto", help="Automatic question answers", default=False),
    )

    def run(self, host, url, timeout, auto):
        print("Connecting to server at %s..." % self.url_format % (host, url))

        while True:
            print("Polling next question...")
            question = self.request_question(host, url)

            if question is not None:
                if auto:
                    answer = random.choice(["This is a generated answer", None])
                else:
                    answer = input(question.properties["question"])
                self.post_answer(host, question.links["answer"].url(), answer)
                print("Answer submitted...")
            else:
                print("No question to answer...")
                print("Going to sleep for %d ms..." % timeout)

            time.sleep(timeout / 1000)

    def request_question(self, host, url):
        response = requests.get(self.url_format % (host, url))

        # No new question
        if response.status_code == 204:
            return None
        # New question
        elif response.status_code == 200:
            try:
                question = dougrain.Document.from_object(response.json())
            except JSONDecodeError:
                raise InvalidQuestionFormatException()

            # Wrong response format
            if not self.is_response_format_valid(question):
                raise InvalidQuestionFormatException()

            # Question received
            self.received_question(host, question.links["received"].url())
        # Wrong status code
        elif response.status_code != 200:
            raise WrongStatusCodeException(response)

        return question

    def is_response_format_valid(self, response):
        if "_id" not in response.properties \
                or "question" not in response.properties:
            return False

        return True

    def received_question(self, host, received_question_url):
        response = requests.post(self.url_format % (host, received_question_url))

        if response.status_code == 204:
            return True
        else:
            raise WrongStatusCodeException(response)

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
