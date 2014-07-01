from httpy.connection.error import UnresolvableHost
from keepon import client


def main():
    response = client.get('http://www.google.com')
    assert response.body

    try:
        client.get('http://www.google.ita')
    except UnresolvableHost:
        pass

    try:
        client.get('http://localhost:9999')
        assert False
    except UnresolvableHost:
        pass

if __name__ == '__main__':
    main()