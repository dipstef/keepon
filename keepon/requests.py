from funlib.retry.sleep import sleep
from httpy.response import ResponseStatus
from httpy_client.requests import HttpRequestDispatch

from funlib.retry import RetryOnErrors
from httpy_client.urrlib import requests

from .attempt import on_incomplete_read, join


class RetryRequests(HttpRequestDispatch):
    def __init__(self, attempts, client=requests):
        super(RetryRequests, self).__init__(client)

        self._attempts = attempts
        self._retry_execute = RetryOnErrors(super(RetryRequests, self)._execute, attempts)

    def _execute(self, request, **kwargs):
        response = self._retry_execute(request, **kwargs)

        return ResponseReadRetry(response, redo_request=self._execute, attempts=self._attempts)


class ResponseReplay(ResponseStatus):

    def __init__(self, response, redo_request):
        super(ResponseReplay, self).__init__(response.request, response.url, response.status, response.headers,
                                             response.date)
        self._replay = redo_request
        self._response = response

    def read(self):
        return self._read()

    def replay(self):
        response = self._replay(self.request)
        return ResponseReplay(response, self._replay)

    def __getattr__(self, item):
        return getattr(self._response, item)


class ResponseReadRetry(ResponseReplay):

    def __init__(self, response, redo_request, attempts):
        super(ResponseReadRetry, self).__init__(response, redo_request)
        self._response = response
        self._read = RetryOnErrors(self._read_body, join(attempts, on_incomplete_read(sleep(2))))

    def read(self):
        return self._read()

    def _read_body(self):
        try:
            return self._response.read()
        except:
            self._response = self._response.replay()
            raise