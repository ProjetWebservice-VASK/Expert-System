import json
import unittest
from dougrain import Builder
import expert_system
import httpretty
from app.question_module.commands.collect_question import CollectQuestion
from app.question_module.exceptions import request_exceptions


class TestCollectQuestion(unittest.TestCase):
    host = "test.com"
    url = "questions/latest"
    answer_url = "question/%d/answer"

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
        request_body = Builder(self.url).set_property("id", 1) \
                                        .set_property("question", "Texte de la question")

        httpretty.register_uri(httpretty.GET, "http://test.com/questions/latest",
                               body=json.dumps(request_body.as_object()),
                               content_type="application/hal+json")

        response = self.collect_question_command.request_question(self.host, self.url)

        self.assertEquals(1, response.properties["id"])
        self.assertEquals("Texte de la question", response.properties["question"])

    @httpretty.activate
    def test_request_question_not_found(self):
        httpretty.register_uri(httpretty.GET, "http://test.com/questions/latest",
                               status=404)

        self.assertRaises(request_exceptions.WrongStatusCodeException,
                          lambda: self.collect_question_command.request_question(self.host, self.url))

    @httpretty.activate
    def test_request_question_but_no_question(self):
        httpretty.register_uri(httpretty.GET, "http://test.com/questions/latest",
                               status=204)

        self.assertRaises(request_exceptions.NoContentException,
                          lambda: self.collect_question_command.request_question(self.host, self.url))

    # Answer posting
    # @httpretty.activate
    # def test_post_answer(self):
    # request = self.collect_question_command.post_answer(self.host, self.answer_url)
    #
    #     self.assertEquals("POST", request.method)


if __name__ == '__main__':
    unittest.main()
