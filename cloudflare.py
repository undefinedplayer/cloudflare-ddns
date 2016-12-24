import sys
import requests


class CloudFlare:
    """
    CloudFlare dns tools
    """
    api_url = 'https://api.cloudflare.com/client/v4/zones/'

    email = ''

    api_key = ''

    headers = None

    domain = None

    zone = None

    dns_records = None

    def __init__(self, email: str, api_key: str, domain: str):
        """
        Initialization. It will set the zone information of the domain for operation.
        It will also get dns records of the current zone.
        :param email:
        :param api_key:
        :param domain:
        """
        self.email = email
        self.api_key = api_key
        self.domain = domain
        self.headers = {
            'X-Auth-Key': api_key,
            'X-Auth-Email': email,
            'Content-Type': 'application/json'
        }

        # Initialize current zone
        zones_content = self.request(self.api_url, 'get')
        try:
            zone = [ zone for zone in zones_content.result if zone.name == domain][0]
        except IndexError:
            print('Cannot find the domain you specified.')
            sys.exit(1)
        self.zone = zone

        # Initialize dns_records of current zone
        dns_content = self.request(self.api_url + '/' + zone.id + '/dns_records', 'get')
        self.dns_records = dns_content.result

    def request(self, url, method, data=None):
        """
        The requester shortcut to submit a http request to CloutFlare
        :param url:
        :param method:
        :param data:
        :return:
        """
        method = getattr(requests, method)
        response = method(url, headers=self.headers, data=data)
        content = response.json()
        if response.status_code != 200:
            raise requests.HTTPError(content.message)
        return content

    def update_record(self, dns_type, name, content, ttl=1, proxied=False):
        """
        Update dns record
        :param dns_type:
        :param name:
        :param content:
        :param ttl:
        :param proxied:
        :return:
        """
        try:
            record = [record for record in self.dns_records if record.type == dns_type and record.name == name][0]
        except IndexError:
            print('Cannot find the specified dns record in domain {domain}'.format(domain=self.domain))
            sys.exit(1)

        data = {content: content}
        if ttl != 1:
            data.ttl = ttl
        if proxied:
            data.proxied = proxied
        self.request(
            self.api_url + '/' + self.zone.id + '/dns_records/' + record.id,
            'put',
            data=data
        )
        print('DNS record successfully updated')




