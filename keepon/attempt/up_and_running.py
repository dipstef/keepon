from funlib.retry.sleep import sleep, incremental_sleep
from httpy_client import HttpClient

from . import on_no_connection, on_unresolvable_host, on_timeouts, on_connection_refused, on_response_error, \
    on_server_error
from ..requests import RetryRequests


up_and_running = (
    on_no_connection(sleep(1)),
    on_unresolvable_host(sleep(1), retry=10),
    on_timeouts(incremental_sleep(1, to=10)),
    on_connection_refused(incremental_sleep(1, to=10)),
    on_response_error(sleep(2), retry=10),
    on_server_error(incremental_sleep(10, to=30), retry=10),
)

requests = RetryRequests(up_and_running)
client = HttpClient(requests)