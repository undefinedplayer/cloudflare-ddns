import requests
import urllib.parse
from exceptions import ZoneNotFound, RecordNotFound


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
            raise ZoneNotFound('Cannot find zone information for the domain {domain}.'.format(domain=domain))
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

    def get_record(self, dns_type, name):
        """
        Get a dns record
        :param dns_type:
        :param name:
        :return:
        """
        try:
            record = [record for record in self.dns_records if record.type == dns_type and record.name == name][0]
        except IndexError:
            return None
        return record

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
        record = [record for record in self.dns_records if record.type == dns_type and record.name == name][0]
        if record is None:
            raise RecordNotFound('Cannot find the specified dns record in domain {domain}'.format(domain=self.domain))

        data = {
            'type': dns_type,
            'name': name,
            'content': content
        }
        if ttl != 1:
            data.ttl = ttl
        if proxied:
            data.proxied = proxied
        self.request(
            urllib.parse.urljoin(self.api_url, self.zone.id, self.zone.id + '/dns_records/' + record.id),
            'put',
            data=data
        )
        print('DNS record successfully updated')

    def create_record(self, dns_type, name, content, ttl=1, proxied=False):
        """
        Create a dns record
        :param dns_type:
        :param name:
        :param content:
        :param ttl:
        :param proxied:
        :return:
        """
        data = {
            'type': dns_type,
            'name': name,
            'content': content
        }
        if ttl != 1:
            data.ttl = ttl
        if proxied:
            data.proxied = proxied
        self.request(
            urllib.parse.urljoin(self.api_url, self.zone.id, self.zone.id + '/dns_records'),
            'put',
            data=data
        )
        print('DNS record successfully created')

    def create_or_update_record(self, dns_type, name, content, ttl=1, proxied=False):
        """
        Create a dns record. Update it if the record already exists.
        :param dns_type:
        :param name:
        :param content:
        :param ttl:
        :param proxied:
        :return:
        """
        try:
            self.update_record(dns_type, name, content, ttl, proxied)
        except IndexError:
            self.create_record(dns_type, name, content, ttl, proxied)
