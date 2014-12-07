class WrongStatusCodeException(Exception):
    def __init__(self, response):
        self.message = response.url + " => The request responded with this status code : " + str(response.status_code) + " - " + response.reason

    def __str__(self):
        return repr(self.message)


class NoContentException(Exception):
    def __init__(self):
        self.message = "The request answered with the status code 204 - No content"

    def __str__(self):
        return repr(self.message)