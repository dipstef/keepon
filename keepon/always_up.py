from connected.error import NoConnection, UnresolvableHost, ConnectionRefused
from funlib.retry.sleep import sleep, increment_sleep
from httpy.error import HttpResponseError
from httpy_client.error import HttpServerError, IncompleteRead
from .attempts import on, Timeouts
from .requests import RetryRequests

up_and_running = (
    on(NoConnection, sleep(1), msg='No Internet connection when resolving {url}'),
    on(UnresolvableHost, sleep(1), msg='Host is unresolvable but internet seem to be up {url}: {error} '),
    on(Timeouts, increment_sleep(1, to=10), msg='Operation timeout: {error} when contacting: {url}'),
    on(ConnectionRefused, increment_sleep(1, to=10), msg='Connection refused: {url}'),
    on(HttpResponseError, sleep(2), retry=10, msg='Server Response error: {error} on {url}'),
    on(HttpServerError, increment_sleep(10, to=30), retry=10, msg='Server connection error: {error} on {url}'),
    on(IncompleteRead, sleep(2), msg='Incomplete response read: {url}')
)

client = RetryRequests(up_and_running)