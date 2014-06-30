from catches import ErrorsHandler
from funlib.retry.retries import AttemptTimes
from httpy.error import HttpServerError, IncompleteRead
from procol.console import print_err

from httpy.connection.error import ConnectionTimeout, NotConnected, UnresolvableHost, ConnectionRefused
from httpy.error import HttpOperationTimeout, HttpResponseError


class RequestAttempt(AttemptTimes):

    def __init__(self, times=None, msg=None, sleep_fun=None):
        super(RequestAttempt, self).__init__(times, self._print_error)
        self.sleep = sleep_fun

        self.msg = msg or 'Error {error} executing {url}'

    def _print_error(self, attempt):
        #error, request = attempt.error, attempt.call.args[1]
        error, request = attempt.error, attempt.error.request

        error_msg = self.msg.format(error=error, error_class=error.__class__, url=request.url)
        if attempt.number > 1:
            error_msg += ', attempted %d times' % attempt.number

        if self.sleep:
            seconds = self.sleep.sleepy_time(attempt)

            print_err(error_msg + ', waiting %d seconds' % seconds)
            self.sleep.zzz(seconds)
        else:
            print_err(error_msg)


def on(errors, sleep=None, retry=None, msg=None):
    return ErrorsHandler(errors, RequestAttempt(retry, msg, sleep))


Timeouts = (HttpOperationTimeout, ConnectionTimeout)


def on_no_connection(sleep=None, retry=None):
    return on(NotConnected, sleep, retry, msg='No Internet connection when resolving {url}')


def on_unresolvable_host(sleep=None, retry=None):
    return on(UnresolvableHost, sleep, retry, msg='Host is unresolvable but internet seem to be up {url}: {error}')


def on_timeouts(sleep=None, retry=None):
    return on(Timeouts, sleep, retry, msg='Operation timeout: {error} when contacting: {url}')


def on_connection_refused(sleep=None, retry=None):
    return on(ConnectionRefused, sleep, retry, msg='Connection refused: {url}')


def on_response_error(sleep=None, retry=None):
    return on(HttpResponseError, sleep, retry, msg='Server Response error: {error} on {url}')


def on_server_error(sleep=None, retry=None):
    return on(HttpServerError, sleep, retry, msg='Server connection error: {error} on {url}')


def on_incomplete_read(sleep=None, retry=None):
    return on(IncompleteRead, sleep, retry, msg='Incomplete response read: {url}')


def join(attempts, *handlers):
    return tuple(list(attempts) + list(handlers))