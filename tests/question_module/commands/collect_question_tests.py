# -*- coding: utf-8 -*-

import json
import unittest
import dougrain
import expert_system
import httpretty
from app.question_module.commands.collect_question import CollectQuestion
from app.question_module.exceptions import request_exceptions


class TestCollectQuestion(unittest.TestCase):
    url_format = "http://%s/%s"
    host = "test.com"
    question_url = "questions/latest"
    answer_url = "question/%d/answer"

    question_id = 1
    question_text = "Texte de la question"
    answer_text = "Texte de la réponse"

    def setUp(self):
        expert_system.app.config['TESTING'] = True
        self.app = expert_system.app.test_client()
        self.collect_question_command = CollectQuestion()

    def tearDown(self):
        httpretty.reset()
        httpretty.disable()

    # Question request
    @httpretty.activate
    def test_request_question_found(self):
        request_body = dougrain.Builder(self.question_url).set_property("id", self.question_id) \
                                        .set_property("question", self.question_text) \
                                        .add_link("answer", self.answer_url % self.question_id)

        httpretty.register_uri(httpretty.GET, self.url_format % (self.host, self.question_url),
                               body=json.dumps(request_body.as_object()),
                               content_type="application/hal+json")

        response = self.collect_question_command.request_question(self.host, self.question_url)

        self.assertEquals(self.question_id, response.properties["id"])
        self.assertEquals(self.question_text, response.properties["question"])

    @httpretty.activate
    def test_request_question_not_found(self):
        httpretty.register_uri(httpretty.GET, self.url_format % (self.host, self.question_url),
                               status=404)

        self.assertRaises(request_exceptions.WrongStatusCodeException,
                          lambda: self.collect_question_command.request_question(self.host, self.question_url))

    @httpretty.activate
    def test_request_question_but_no_question(self):
        httpretty.register_uri(httpretty.GET, self.url_format % (self.host, self.question_url),
                               status=204)

        self.assertRaises(request_exceptions.NoContentException,
                          lambda: self.collect_question_command.request_question(self.host, self.question_url))

    # Answer creation
    @httpretty.activate
    def test_create_answer_request(self):
        request = self.collect_question_command.create_answer_request(self.host, self.answer_url % self.question_id, self.answer_text)

        expected_answer_json = {
            "answer": self.answer_text
        }

        self.assertEquals("PUT", request.method)
        self.assertEquals(self.url_format % (self.host, self.answer_url % self.question_id), request.url)
        self.assertEquals(expected_answer_json, request.json)


if __name__ == '__main__':
    unittest.main()
