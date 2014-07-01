from keepon import client

response = client.get('http://www.repubblica.it')
print response
print response.body