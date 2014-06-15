from funlib.retry.sleep import sleep

from httpy_client import HttpClient
from . import on_unresolvable_host
from .up_and_running import up_and_running
from ..requests import RetryRequests


always_up = list(up_and_running)
always_up[1] = on_unresolvable_host(sleep(1), retry=10)


requests = RetryRequests(up_and_running)
client = HttpClient(requests)