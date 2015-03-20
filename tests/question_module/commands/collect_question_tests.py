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

    latest_question_url = "questions/next"
    received_question_url = "questions/%d/received"

    answer_url = "question/%d/answer"
    unknown_answer_url = "question/%d/answer"

    question_url = "questions/%d"
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
        request_body = json.dumps({
            "question": {
                "_id": self.question_id,
                "question": self.question_text,
            },
            "_links": {
                "received": self.received_question_url % self.question_id,
                "answer": self.answer_url % self.question_id
            }
        })

        # Latest question volatile url
        httpretty.register_uri(httpretty.GET, self.url_format % (self.host, self.latest_question_url),
                               location=self.url_format % (self.host, self.question_url % self.question_id),
                               status=307)

        # Question resource url
        httpretty.register_uri(httpretty.GET, self.url_format % (self.host, self.question_url % self.question_id),
                               body=request_body,
                               content_type="application/hal+json")

        # Well received question url
        httpretty.register_uri(httpretty.POST, self.url_format % (self.host, self.received_question_url % self.question_id),
                               status=204)

        response = self.collect_question_command.request_question(self.host, self.latest_question_url)

        self.assertEquals(self.question_id, response["question"]["_id"])
        self.assertEquals(self.question_text, response["question"]["question"])
        self.assertEquals(self.answer_url % self.question_id, response["_links"]["answer"])

    # Question received
    @httpretty.activate
    def test_request_question_received(self):
        httpretty.register_uri(httpretty.POST, self.url_format % (self.host, self.received_question_url % self.question_id),
                               status=204)

        self.assertTrue(self.collect_question_command.received_question(self.host, self.received_question_url % self.question_id))

    @httpretty.activate
    def test_request_question_received_with_bad_response(self):
        httpretty.register_uri(httpretty.POST, self.url_format % (self.host, self.received_question_url % self.question_id),
                               status=404)

        self.assertRaises(request_exceptions.WrongStatusCodeException,
                          lambda: self.collect_question_command.received_question(self.host, self.received_question_url % self.question_id))

    # Question format
    def test_is_response_format_valid_with_valid_response(self):
        response = {
            "question": {
                "_id": self.question_id,
                "question": self.question_text,
            },
            "_links": {
                "received": self.received_question_url % self.question_id,
                "answer": self.answer_url % self.question_id
            }
        }

        self.assertTrue(self.collect_question_command.is_response_format_valid(response))

    def test_is_response_format_valid_with_invalid_response(self):
        response = {
            "question": {},
            "_links": {
                "received": self.received_question_url % self.question_id,
                "answer": self.answer_url % self.question_id
            }
        }

        self.assertFalse(self.collect_question_command.is_response_format_valid(response))

    @httpretty.activate
    def test_request_question_not_found(self):
        httpretty.register_uri(httpretty.GET, self.url_format % (self.host, self.latest_question_url),
                               status=404)

        self.assertRaises(request_exceptions.WrongStatusCodeException,
                          lambda: self.collect_question_command.request_question(self.host, self.latest_question_url))

    @httpretty.activate
    def test_request_question_but_no_question(self):
        httpretty.register_uri(httpretty.GET, self.url_format % (self.host, self.latest_question_url),
                               status=204)

        self.assertEquals(None, self.collect_question_command.request_question(self.host, self.latest_question_url))

    @httpretty.activate
    def test_request_question_wrong_page(self):
        response = {
            "_id": self.question_id,
            "dog": "woof",
            "_links": {
                "cat": "meow"
            }
        }

        httpretty.register_uri(httpretty.GET, self.url_format % (self.host, self.latest_question_url),
                               body=response,
                               content_type="application/hal+json")

        self.assertRaises(request_exceptions.InvalidQuestionFormatException,
                          lambda: self.collect_question_command.request_question(self.host, self.latest_question_url))

    # Answer creation
    def test_create_answer_request(self):
        request = self.collect_question_command.create_answer_request(self.host, self.answer_url % self.question_id,
                                                                      self.answer_text)

        expected_answer_json = {
            "answer": self.answer_text
        }

        self.assertEquals("PUT", request.method)
        self.assertEquals(self.url_format % (self.host, self.answer_url % self.question_id), request.url)
        self.assertEquals(expected_answer_json, request.json)

    def test_create_unknown_answer_request(self):
        request = self.collect_question_command.create_answer_request(self.host,
                                                                      self.unknown_answer_url % self.question_id, None)

        self.assertEquals("PUT", request.method)
        self.assertEquals(self.url_format % (self.host, self.unknown_answer_url % self.question_id), request.url)
        self.assertEquals(None, request.json)

    # Posting answer
    @httpretty.activate
    def test_post_answer(self):
        httpretty.register_uri(httpretty.PUT, self.url_format % (self.host, self.answer_url % self.question_id),
                               status=204)

        self.assertTrue(
            self.collect_question_command.post_answer(self.host, self.answer_url % self.question_id, self.answer_text))

    @httpretty.activate
    def test_post_answer_with_error(self):
        httpretty.register_uri(httpretty.PUT, self.url_format % (self.host, self.answer_url % self.question_id),
                               status=404)

        self.assertRaises(request_exceptions.WrongStatusCodeException,
                          lambda: self.collect_question_command.post_answer(self.host,
                                                                            self.answer_url % self.question_id,
                                                                            self.answer_text))


if __name__ == '__main__':
    unittest.main()
