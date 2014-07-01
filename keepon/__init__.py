from httpy import HttpClient, requests

from .attempt import *
from .requests import RetryRequests, ResponseReplay
from .up_and_running import up_and_running


class Keepon(HttpClient):

    def __init__(self, *attempts):
        super(Keepon, self).__init__(RetryRequests(attempts))


requests = RetryRequests(up_and_running)
client = HttpClient(requests)