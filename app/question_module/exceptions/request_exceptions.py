class WrongStatusCodeException(Exception):
    def __init__(self, status_code):
        self.message = "The request responded with this status code : " + str(status_code)

    def __str__(self):
        return repr(self.message)


class NoContentException(Exception):
    def __init__(self):
        self.message = "The request answered with the status code 204 - No content"

    def __str__(self):
        return repr(self.message)