from funlib.retry.sleep import sleep

from . import on_unresolvable_host, up_and_running
from ..requests import RetryRequests


always_up = tuple(up_and_running)
always_up[1] = on_unresolvable_host(sleep(1), retry=10),


client = RetryRequests(up_and_running)