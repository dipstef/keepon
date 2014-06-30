from funlib.retry.sleep import sleep
from httpy import HttpClient

from . import on_no_connection, on_unresolvable_host
from ..requests import RetryRequests


_attempts = (
    on_no_connection(sleep(1)),
    on_unresolvable_host(sleep(1), retry=10),
)

requests = RetryRequests(_attempts)
client = HttpClient(requests)