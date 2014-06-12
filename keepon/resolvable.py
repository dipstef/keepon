from connected.error import NoConnection, UnresolvableHost
from funlib.retry.sleep import sleep
from .attempts import on
from .requests import RetryRequests

_attempts = (
    on(NoConnection, sleep(1), msg='No Internet connection when resolving {url}'),
    on(UnresolvableHost, sleep(1), retry=10, msg='Host is unresolvable but internet seem to be up {url}: {error} '),
)

client = RetryRequests(_attempts)