from funlib.retry.sleep import sleep
from keepon import on_no_connection, Keepon

#client = Keepon(on_no_connection(sleep=sleep(1), retry=10))

#client.get('http://www.google.com')