class WrongStatusCodeException(Exception):
    def __init__(self, response):
        self.message = response.url + " => The request responded with this status code : " + str(response.status_code) + " - " + response.reason

    def __str__(self):
        return repr(self.message)


class InvalidQuestionFormatException(Exception):
    def __init__(self):
        self.message = "The question format isn't respected check the request's content-type and content"

    def __str__(self):
        return repr(self.message)