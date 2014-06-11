from httpy.response import ResponseStatus
from httpy_client import http_client
from httpy_client.requests import HttpRequestDispatch
from funlib.retry import retry_on_errors
from keepon.attempts import server_must_be_up


class RetryRequests(HttpRequestDispatch):
    _attempts = server_must_be_up

    @retry_on_errors(*_attempts)
    def _execute(self, request, **kwargs):
        response = super(RetryRequests, self)._execute(request, **kwargs)
        return ResponseReadRetry(response, self, self._attempts)


class ResponseReadRetry(ResponseStatus):

    def __init__(self, response, requests, error_attempts):
        super(ResponseReadRetry, self).__init__(response.request, response.url, response.status, response.headers,
                                                response.date)
        self._response = response
        self._requests = requests
        self._attempts = error_attempts

    @property
    def body(self):
        return self._get_body(error_handlers=self._attempts)

    @retry_on_errors
    def _get_body(self):
        try:
            return self._response.body
        except:
            self._response = self._redo_request(error_handlers=self._attempts)
            raise

    @retry_on_errors
    def _redo_request(self):
        return self._requests._execute(self.request)

    def __getattr__(self, item):
        return getattr(self._response, item)

client = RetryRequests(http_client)


def main():
    response = client.get('http://www.repubblica.it')
    assert response.body

    client.get('http://localhost:9999')

if __name__ == '__main__':
    main()