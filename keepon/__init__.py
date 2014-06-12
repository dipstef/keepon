from .attempt.up_and_running import up_and_running
from .requests import RetryRequests

client = RetryRequests(up_and_running)