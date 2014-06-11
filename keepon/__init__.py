from connected.error import ConnectionTimeout, NoConnection, UnresolvableHost, ConnectionRefused
from procol.console import print_err

from httpy.error import HttpOperationTimeout, HttpResponseError
from httpy.response import ResponseStatus

from httpy_client import http_client
from httpy_client.error import HttpServerError, IncompleteRead
from httpy_client.requests import HttpRequestDispatch

from funlib.retry import retry_on_errors
from funlib.retry.retries import AttemptTimes
from funlib.retry.sleep import sleep


class RequestAttempt(AttemptTimes):

    def __init__(self, times=None, msg=None, seconds=None):
        super(RequestAttempt, self).__init__(times, self._print_error, sleep=sleep(seconds) if sleep else None)

        self._msg = msg or 'Error {error} executing {url}'
        if seconds:
            self._msg += ', waiting %d seconds' % seconds

    def _print_error(self, attempt):
        #error, request = attempt.error, attempt.call.args[1]
        error, request = attempt.error, attempt.error.request
        error_msg = self._msg.format(error=error, error_class=error.__class__, url=request.url)
        if attempt.number > 1:
            error_msg += ', attempted %d times' % attempt.number
        print_err(error_msg)


def _on(errors, retry=None, msg=None, sleep=None):
    return errors, RequestAttempt(retry, msg, sleep)


attempts = (
    _on(NoConnection, sleep=1, msg='No Internet connection when resolving {url}'),
    _on(UnresolvableHost, retry=10, sleep=1, msg='Host is unresolvable but internet seem to be {url}: {error} '),
    _on((HttpOperationTimeout, ConnectionTimeout), sleep=2, msg='Operation timeout: {error} when contacting: {url}'),
    _on(ConnectionRefused, sleep=1, msg='Connection refused: {url}'),
    _on(HttpResponseError, retry=10, sleep=2, msg='Server Response error: {error} on {url}'),
    _on(HttpServerError, retry=10, sleep=30, msg='Server connection error: {error} on {url}'),
    _on(IncompleteRead, sleep=2, msg='Incomplete response read: {url}')
)


class RetryRequests(HttpRequestDispatch):
    _attempts = attempts

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