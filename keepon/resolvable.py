from funlib.retry.sleep import sleep

from .attempts import on_no_connection, on_unresolvable_host
from .requests import RetryRequests


_attempts = (
    on_no_connection(sleep(1)),
    on_unresolvable_host(sleep(1), retry=10),
)

client = RetryRequests(_attempts)