from funlib.retry.retries import AttemptTimes
from funlib.retry.sleep import sleep
from procol.console import print_err

from connected.error import ConnectionTimeout, NoConnection, UnresolvableHost, ConnectionRefused
from httpy.error import HttpOperationTimeout, HttpResponseError
from httpy_client.error import HttpServerError, IncompleteRead


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


server_must_be_up = (
    _on(NoConnection, sleep=1, msg='No Internet connection when resolving {url}'),
    _on(UnresolvableHost, retry=10, sleep=1, msg='Host is unresolvable but internet seem to be {url}: {error} '),
    _on((HttpOperationTimeout, ConnectionTimeout), sleep=2, msg='Operation timeout: {error} when contacting: {url}'),
    _on(ConnectionRefused, sleep=1, msg='Connection refused: {url}'),
    _on(HttpResponseError, retry=10, sleep=2, msg='Server Response error: {error} on {url}'),
    _on(HttpServerError, retry=10, sleep=30, msg='Server connection error: {error} on {url}'),
    _on(IncompleteRead, sleep=2, msg='Incomplete response read: {url}')
)
