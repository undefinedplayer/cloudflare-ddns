==========
CloudFlare
==========

The Python DDNS(Dynamic DNS) script for CloudFlare. It can sync your public IP address to DNS records on CloudFlare. It also provide the RESTful API to operate CloudFlare API v4.

Examples
--------

1. Sync your public ip address to dns record on CloudFlare

import CloudFlare from cloudflare

.. code:: python

    cf = CloudFlare(your_email, your_api_key, 'example.com')
    cf.sync_dns_from_my_ip() #Successfully updated IP address from xx.xx.xx.xx to xx.xx.xx.xx

2. RESTful dns record operation

.. code:: python

    cf.get_record('A', 'sub.example.com')

.. code:: python

    cf.create_record('A', 'sub.example.com', '202.202.202.202')

.. code:: python

    cf.update_record('A', 'sub.example.com', '202.202.202.202')

.. code:: python

    cf.delete_record('A', 'sub.example.com')

*Please note: The class will cache dns records information it gets from CloudFlare. To refresh cache, use 'refresh' method:*

.. code:: python

    cf.refresh()
