===============
cloudflare-ddns
===============

The Python DDNS(Dynamic DNS) script for CloudFlare. It can sync your public IP address to DNS records on CloudFlare. It also provide the RESTful API to operate CloudFlare API v4.

Installation
------------

.. code:: shell

    pip install cloudflare-ddns

Examples
--------

#. Sync your public ip address to dns record on CloudFlare

    - Use command in command line

    .. code:: shell

        cloudflare-ddns email api_key domain

    - Execute python package in command line

    .. code:: shell

        python -m cloudflare_ddns email api_key domain


    - Python code

    .. code:: python

        from cloudflare_ddns import CloudFlare
        cf = CloudFlare(email, api_key, domain)
        cf.sync_dns_from_my_ip() # Successfully updated IP address from xx.xx.xx.xx to xx.xx.xx.xx

#. RESTful dns record operation

.. code:: python

    cf.get_record('A', 'example.com')

.. code:: python

    cf.create_record('A', 'sub.example.com', '202.202.202.202')

.. code:: python

    cf.update_record('A', 'another.example.com', '202.202.202.202')

.. code:: python

    cf.delete_record('A', 'another.example.com')

*Please note: The class will cache dns records information it gets from CloudFlare. To refresh cache, call 'refresh' method:*

.. code:: python

    cf.refresh()
