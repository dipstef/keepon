from keepon import client


def main():
    response = client.get('http://www.repubblica.it')
    assert response.body

    client.get('http://localhost:9999')

if __name__ == '__main__':
    main()