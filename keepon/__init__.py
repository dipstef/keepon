from httpy.response import ResponseStatus
from httpy_client import http_client
from httpy_client.requests import HttpRequestDispatch
from funlib.retry import RetryOnErrors

from keepon.attempts import up_and_running


class RetryRequests(HttpRequestDispatch):
    def __init__(self, request_handler, attempt_on=up_and_running):
        super(RetryRequests, self).__init__(request_handler)

        self._attempts = attempt_on
        self._retry_execute = RetryOnErrors(super(RetryRequests, self)._execute, attempt_on)

    def _execute(self, request, **kwargs):
        response = self._retry_execute(request, **kwargs)

        return ResponseReadRetry(response, redo_request=self._execute, attempts_handlers=self._attempts)


class ResponseReplay(ResponseStatus):

    def __init__(self, response, redo_request):
        super(ResponseReplay, self).__init__(response.request, response.url, response.status, response.headers,
                                             response.date)
        self._replay = redo_request
        self._response = response

    @property
    def body(self):
        return self._response.body

    def replay(self):
        response = self._replay(self.request)
        return ResponseReplay(response, self._replay)

    def __getattr__(self, item):
        return getattr(self._response, item)


class ResponseReadRetry(ResponseReplay):

    def __init__(self, response, redo_request, attempts_handlers):
        super(ResponseReadRetry, self).__init__(response, redo_request)
        self._response = response

        self._get_body = RetryOnErrors(self._read_body, attempts_handlers)


    @property
    def body(self):
        return self._get_body()

    def _read_body(self):
        try:
            return self._response.body
        except:
            self._response = self._response.replay()
            raise

client = RetryRequests(http_client)


def main():
    response = client.get('http://www.repubblica.it')
    assert response.body

    client.get('http://localhost:9999')

if __name__ == '__main__':
    main()