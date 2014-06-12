from funlib.retry.retries import AttemptTimes
from procol.console import print_err

from connected.error import ConnectionTimeout
from httpy.error import HttpOperationTimeout


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


def on(errors, sleep=None, retry=None, msg=None):
    return errors, RequestAttempt(retry, msg, sleep)


Timeouts = (HttpOperationTimeout, ConnectionTimeout)