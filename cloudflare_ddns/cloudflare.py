"""
CloudFlare dns tools.
"""
import sys
import argparse
import socket
import urllib.parse
import requests
from .exceptions import ZoneNotFound, RecordNotFound


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('email')
    parser.add_argument('api_key')
    parser.add_argument('domain')
    args = parser.parse_args()
    cf = CloudFlare(**vars(args))
    cf.sync_dns_from_my_ip()


class CloudFlare:
    """
    CloudFlare dns tools class
    """
    api_url = 'https://api.cloudflare.com/client/v4/zones/'

    email = ''

    api_key = ''

    headers = None

    domain = None

    zone = None

    dns_records = None

    public_ip_finder = (
        'https://api.ipify.org/',
        'https://jsonip.com/',
        'https://ifconfig.co/json'
    )

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
        self.setup_zone()

    def request(self, url, method, data=None):
        """
        The requester shortcut to submit a http request to CloutFlare
        :param url:
        :param method:
        :param data:
        :return:
        """
        method = getattr(requests, method)
        response = method(
            url,
            headers=self.headers,
            data=self.process_json_for_cloudflare(data)
        )
        content = response.json()
        if response.status_code != 200:
            print(content)
            raise requests.HTTPError(content['message'])
        return content

    def setup_zone(self):
        """
        Setup zone for current domain.
        It will also setup the dns records of the zone
        :return:
        """
        # Initialize current zone
        zones_content = self.request(self.api_url, 'get')
        try:
            zone = [zone for zone in zones_content['result'] if zone['name'] == self.domain][0]
        except IndexError:
            raise ZoneNotFound('Cannot find zone information for the domain {domain}.'
                               .format(domain=self.domain))
        self.zone = zone

        # Initialize dns_records of current zone
        dns_content = self.request(self.api_url + '/' + zone['id'] + '/dns_records', 'get')
        self.dns_records = dns_content['result']

    def refresh(self):
        """
        Shortcut for setup zone
        :return:
        """
        self.setup_zone()

    def get_record(self, dns_type, name):
        """
        Get a dns record
        :param dns_type:
        :param name:
        :return:
        """
        try:
            record = [record for record in self.dns_records
                      if record['type'] == dns_type and record['name'] == name][0]
        except IndexError:
            raise RecordNotFound(
                'Cannot find the specified dns record in domain {domain}'
                .format(domain=self.domain))
        return record

    def create_record(self, dns_type, name, content, **kwargs):
        """
        Create a dns record
        :param dns_type:
        :param name:
        :param content:
        :param kwargs:
        :return:
        """
        data = {
            'type': dns_type,
            'name': name,
            'content': content
        }
        if kwargs.get('ttl') and kwargs['ttl'] != 1:
            data['ttl'] = kwargs['ttl']
        if kwargs.get('proxied') is False:
            data['proxied'] = False
        else:
            data['proxied'] = True
        content = self.request(
            urllib.parse.urljoin(self.api_url, self.zone['id'], self.zone['id'] + '/dns_records'),
            'put',
            data=data
        )
        print('DNS record successfully created')
        return content['result']

    def update_record(self, dns_type, name, content, **kwargs):
        """
        Update dns record
        :param dns_type:
        :param name:
        :param content:
        :param kwargs:
        :return:
        """
        record = self.get_record(dns_type, name)
        data = {
            'type': dns_type,
            'name': name,
            'content': content
        }
        if kwargs.get('ttl') and kwargs['ttl'] != 1:
            data['ttl'] = kwargs['ttl']
        if kwargs.get('proxied') is False:
            data['proxied'] = False
        else:
            data['proxied'] = True
        content = self.request(
            urllib.parse.urljoin(self.api_url, self.zone['id'] + '/dns_records/' + record['id']),
            'put',
            data=data
        )
        print('DNS record successfully updated')
        return content['result']

    def create_or_update_record(self, dns_type, name, content, **kwargs):
        """
        Create a dns record. Update it if the record already exists.
        :param dns_type:
        :param name:
        :param content:
        :param kwargs:
        :return:
        """
        try:
            return self.update_record(dns_type, name, content, **kwargs)
        except RecordNotFound:
            return self.create_record(dns_type, name, content, **kwargs)

    def delete_record(self, dns_type, name):
        """
        Delete a dns record
        :param dns_type:
        :param name:
        :return:
        """
        record = self.get_record(dns_type, name)
        content = self.request(
            urllib.parse.urljoin(self.api_url, self.zone['id'] + '/dns_records/' + record['id']),
            'delete'
        )
        return content['result']['id']

    def sync_dns_from_my_ip(self, dns_type='A'):
        """
        Sync dns from my public ip address.
        It will not do update if ip address in dns record is already same as
        current public ip address.
        :param dns_type:
        :return:
        """
        ip_address = ''
        for finder in self.public_ip_finder:
            try:
                result = requests.get(finder)
            except requests.RequestException:
                continue
            if result.status_code == 200:
                try:
                    socket.inet_aton(result.text)
                    ip_address = result.text
                    break
                except socket.error:
                    try:
                        socket.inet_aton(result.json().get('ip'))
                        ip_address = result.json()['ip']
                        break
                    except socket.error:
                        continue

        if ip_address == '':
            print('None of public ip finder is working. Please try later')
            sys.exit(1)
        record = self.get_record(dns_type, self.zone['name'])
        if record['content'] != ip_address:
            self.update_record(dns_type, self.zone['name'], ip_address)
            print('Successfully updated IP address from {old_ip} to {new_ip}'
                  .format(old_ip=record['content'], new_ip=ip_address))
        else:
            print('IP address on CloudFlare is same as your current address')

    @staticmethod
    def process_json_for_cloudflare(data_dict):
        """
        Need to process the data because of the odd format requirement from CloudFlare
        :param data_dict:
        :return:
        """
        return str(data_dict).replace('"', 'double_quote').replace("'", '"').replace('double_quote', "'")
