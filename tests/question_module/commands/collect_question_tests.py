import unittest
import expert_system
import mock
from app.question_module.commands.collect_question import CollectQuestion
from app.question_module.exceptions import request_exceptions
import requests


class TestCollectQuestion(unittest.TestCase):
    host = "127.0.0.1"
    url = "questions/latest"

    def setUp(self):
        expert_system.app.config['TESTING'] = True
        self.app = expert_system.app.test_client()
        self.collect_question_command = CollectQuestion()

    def test_request_question_found(self):
        response = requests.Response()
        response.status_code = 200
        response._content = "Texte de la question"
        requests.get = mock.Mock(return_value=response)

        self.assertEquals("Texte de la question", self.collect_question_command.request_question(self.host, self.url))

    def test_request_question_not_found(self):
        response = requests.Response()
        response.status_code = 404
        requests.get = mock.Mock(return_value=response)

        self.assertRaises(request_exceptions.WrongStatusCodeException,
                          lambda: self.collect_question_command.request_question(self.host, self.url))

    def test_request_question_but_no_question(self):
        response = requests.Response()
        response.status_code = 204
        requests.get = mock.Mock(return_value=response)

        self.assertRaises(request_exceptions.NoContentException,
                          lambda: self.collect_question_command.request_question(self.host, self.url))


if __name__ == '__main__':
    unittest.main()
