from funlib.retry.sleep import sleep
from httpy import HttpClient

from .attempt import on_no_connection, on_unresolvable_host
from .requests import RetryRequests


resolvable = (
    on_no_connection(sleep(1)),
    on_unresolvable_host(sleep(1), retry=10),
)

requests = RetryRequests(resolvable)
client = HttpClient(requests)