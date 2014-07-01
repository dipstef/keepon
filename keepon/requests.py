from funlib.retry import RetryOnErrors
from funlib.retry.sleep import sleep
from httpy import requests, ResponseStatus
from httpy.client.requests import HttpRequestDispatch
from .attempt import join, on_incomplete_read


class RetryRequests(HttpRequestDispatch):
    def __init__(self, attempts, client=requests):
        super(RetryRequests, self).__init__(client)

        self._attempts = attempts
        self._retry_execute = RetryOnErrors(super(RetryRequests, self).execute, attempts)

    def execute(self, request, **kwargs):
        response = self._retry_execute(request, **kwargs)

        return ResponseReadRetry(response, redo_request=self.execute, attempts=self._attempts)


class ResponseReplay(ResponseStatus):

    def __init__(self, response, redo_request):
        super(ResponseReplay, self).__init__(response.request, response.url, response.status, response.headers,
                                             response.date)
        self._replay = redo_request
        self._response = response

    def read(self):
        return self._response.read()

    def _redo_request(self):
        self._response = self._replay(self.request)

    def __getattr__(self, item):
        return getattr(self._response, item)


class ResponseReadRetry(ResponseReplay):

    def __init__(self, response, redo_request, attempts):
        super(ResponseReadRetry, self).__init__(response, redo_request)
        self._response = response
        self.read = RetryOnErrors(self._read_body, join(attempts, on_incomplete_read(sleep(2))))

    def _read_body(self):
        try:
            return self._response.read()
        except:
            self._redo_request()
            raise