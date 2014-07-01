Keepon
======
A client for gently scraping web sites

Features
========
Retries executing http requests until completion (or failed by a maximum number of times).

Handles common http errors such timeouts, disconnections, overloaded host or temporary down.

Slows down requests execution on timeout, overloaded sites.

Built on top of ``httpy`` and ``funlib`` retry and ``catches``.

Usage
=====
Same interface as ``requests``.


.. code-block:: python

    from keepon import on_no_connection, Keepon
    from funlib.retry.sleep import sleep

    >>> client = Keepon(on_no_connection(sleep=sleep(1)))

    #assuming you are disconnected
    >>> client.get('http://www.google.com')
     '''No Internet connection when resolving http://www.google.com, waiting 1 seconds
        No Internet connection when resolving http://www.google.com, attempted 2 times, waiting 1 seconds
        No Internet connection when resolving http://www.google.com, attempted 3 times, waiting 1 seconds
        No Internet connection when resolving http://www.google.com, attempted 4 times, waiting 1 seconds'''

Setting a maximum number of retries

.. code-block:: python

    >>> client = Keepon(on_no_connection(sleep=sleep(1), retry=10))
    >>> client.get('http://www.google.com')
     '''No Internet connection when resolving http://www.google.com, waiting 1 seconds
        ....
        No Internet connection when resolving http://www.google.com, attempted 8 times, waiting 1 seconds
        No Internet connection when resolving http://www.google.com, attempted 9 times, waiting 1 seconds
        No Internet connection when resolving http://www.google.com, attempted 10 times, waiting 1 seconds'''

        httpy.error.NotConnected('[Errno GET: http://www.google.com]')

Increment sleeping time on each attempt

.. code-block:: python

    from funlib.retry.sleep import incremental_sleep

     >>> client = Keepon(on_no_connection(sleep=sleep(1), retry=10),
                         on_timeouts(incremental_sleep(1, to=10)))

     >>> client.get('http://www.twitter.com')
     '''Operation timeout: ('HTTP Error 502: SiteOverloaded') when contacting: http://twitter.com, waiting 1 seconds
        Operation timeout: ('HTTP Error 502: SiteOverloaded') when contacting: http://twitter.com, attempted 2 times, waiting 2 seconds
        Operation timeout: ('HTTP Error 502: SiteOverloaded') when contacting: http://twitter.com, attempted 3 times, waiting 3 seconds
        Operation timeout: ('HTTP Error 502: SiteOverloaded') when contacting: http://twitter.com, attempted 4 times, waiting 4 seconds'''


Attempts
========
Predefined classes of attempts:

Resolvable: A server is probably up (and resolvable) but our internet connection is not so stable

.. code-block:: python

    from keepon.attempt import *


    resolvable = (
        on_no_connection(sleep(1)),
        on_unresolvable_host(sleep(1), retry=10),
    )



Up and running: the server should be up and running and should be able to complete any request

.. code-block:: python

    up_and_running = (
        on_no_connection(sleep(1)),
        on_unresolvable_host(sleep(1), retry=10),
        on_timeouts(incremental_sleep(1, to=10)),
        on_connection_refused(incremental_sleep(1, to=10)),
        on_response_error(sleep(2), retry=10),
        on_server_error(incremental_sleep(10, to=30), retry=10),
    )

Dammit: We are absolutely sure the server is always up, but might have down times (like site updates or overloads)

.. code-block:: python

    dammit = (
        on_no_connection(sleep(1)),
        on_internal_server_error(incremental_sleep(5, to=60)),
        on_unresolvable_host(sleep(1)),
        on_timeouts(incremental_sleep(1, to=10)),
        on_connection_refused(incremental_sleep(1, to=10)),
        on_response_error(sleep(2), retry=10),
        on_server_error(incremental_sleep(10, to=30), retry=10),
    )

.. code-block:: python

    from keepon.resolvable import client
    from keepon.up_and_running import client
    from keepon.dammit import client


Custom attempt classes:

See the ``catches`` documentation for how to build custom error handlers:

 .. code-block:: python

    from keepon import attempt
    from httpy.error import ConnectionResetByPeer, IncompleteRead

    handler = attempt.on(ConnectionResetByPeer, sleep=sleep(10), retry=2, msg='Connection reset when contacting {url}'

    handler = attempt.on((ConnectionResetByPeer, IncompleteRead), sleep=sleep(10), retry=2, msg='Better give up on {url}'