from httpy.client import HttpClient
from .attempt.up_and_running import up_and_running
from .requests import RetryRequests

requests = RetryRequests(up_and_running)
client = HttpClient(requests)