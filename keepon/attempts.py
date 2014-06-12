from funlib.retry.retries import AttemptTimes
from funlib.retry.sleep import sleep, increment_sleep
from procol.console import print_err

from connected.error import ConnectionTimeout, NoConnection, UnresolvableHost, ConnectionRefused
from httpy.error import HttpOperationTimeout, HttpResponseError
from httpy_client.error import HttpServerError, IncompleteRead


class RequestAttempt(AttemptTimes):

    def __init__(self, times=None, msg=None, sleep_fun=None):
        super(RequestAttempt, self).__init__(times, self._print_error)
        self._sleep = sleep_fun

        self._msg = msg or 'Error {error} executing {url}'

    def _print_error(self, attempt):
        #error, request = attempt.error, attempt.call.args[1]
        error, request = attempt.error, attempt.error.request

        error_msg = self._msg.format(error=error, error_class=error.__class__, url=request.url)
        if attempt.number > 1:
            error_msg += ', attempted %d times' % attempt.number

        if self._sleep:
            seconds = self._sleep.sleepy_time(attempt)

            print_err(error_msg + ', waiting %d seconds' % seconds)
            self._sleep.zzz(seconds)
        else:
            print_err(error_msg)


def _on(errors, sleep=None, retry=None, msg=None):
    return errors, RequestAttempt(retry, msg, sleep)


def _attempts(*handlers):
    return tuple(_on(*handler) for handler in handlers)

Timeouts = (HttpOperationTimeout, ConnectionTimeout)

resolvable = (
    _on(NoConnection, sleep(1), msg='No Internet connection when resolving {url}'),
    _on(UnresolvableHost, sleep(1), retry=10, msg='Host is unresolvable but internet seem to be up {url}: {error} '),
)


up_and_running = (
    _on(NoConnection, sleep(1), msg='No Internet connection when resolving {url}'),
    _on(UnresolvableHost, sleep(1), retry=10, msg='Host is unresolvable but internet seem to be up {url}: {error} '),
    _on(Timeouts, increment_sleep(1, to=10), msg='Operation timeout: {error} when contacting: {url}'),
    _on(ConnectionRefused, increment_sleep(1, to=10), msg='Connection refused: {url}'),
    _on(HttpResponseError, sleep(2), retry=10, msg='Server Response error: {error} on {url}'),
    _on(HttpServerError, increment_sleep(10, to=30), retry=10, msg='Server connection error: {error} on {url}'),
    _on(IncompleteRead, sleep(2), msg='Incomplete response read: {url}')
)