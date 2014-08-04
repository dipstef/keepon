from catches import handle, execute
from httpy import HttpRequest
from httpy.connection.error import ConnectionTimeout
from httpy.error import HttpServerSocketError, HttpServerError, HttpError


def _return(value):
    def return_value(*args):
        return value

    return return_value

_request = HttpRequest('GET', 'http://test.com')

_catches = (handle(ConnectionTimeout).doing(_return(1)),
            handle(HttpServerError).doing(_return(2)),
            handle(HttpError).doing(_return(3)))


def _raise(error):
    def raise_error():
        raise error
    return raise_error


class HttpServerConnectionTimeout(HttpServerError, ConnectionTimeout):

    def __init__(self, request):
        super(HttpServerConnectionTimeout, self).__init__(request, ConnectionTimeout())


def main():
    assert execute(_raise(HttpServerSocketError(_request, ConnectionTimeout())), catch=_catches) == 1
    assert execute(_raise(HttpServerConnectionTimeout(_request)), catch=_catches) == 1

    assert execute(_raise(HttpServerError(_request)), catch=_catches) == 2
    assert execute(_raise(HttpError(_request)), catch=_catches) == 3


if __name__ == '__main__':
    main()