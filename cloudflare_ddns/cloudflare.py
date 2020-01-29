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
    parser.add_argument('--proxied', '-p', dest='proxied', action='store_true', default=False,
                        help='Enable the Cloudflare proxy for the record')
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

    proxied = False

    headers = None

    domain = None

    zone = None

    dns_records = None

    public_ip_finder = (
        'https://api.ipify.org/',
        'https://jsonip.com/',
        'https://ifconfig.co/json'
    )

    def __init__(self, email: str, api_key: str, domain: str, proxied: bool = False):
        """
        Initialization. It will set the zone information of the domain for operation.
        It will also get dns records of the current zone.
        :param email:
        :param api_key:
        :param domain:
        :param proxied:
        """
        self.email = email
        self.api_key = api_key
        self.domain = domain
        self.proxied = proxied
        self.headers = {
            'X-Auth-Key': api_key,
            'X-Auth-Email': email
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
            json=data
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
            if len(self.domain.split('.')) == 3:
                domain = self.domain.split('.', 1)[1]
            else:
                domain = self.domain
            zone = [zone for zone in zones_content['result'] if zone['name'] == domain][0]
        except IndexError:
            raise ZoneNotFound('Cannot find zone information for the domain {domain}.'
                               .format(domain=self.domain))
        self.zone = zone

        # Initialize dns_records of current zone
        dns_content = self.request(self.api_url + zone['id'] + '/dns_records', 'get')
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
                .format(domain=name))
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
        if kwargs.get('proxied') is True:
            data['proxied'] = True
        else:
            data['proxied'] = False
        content = self.request(
            self.api_url + self.zone['id'] + '/dns_records',
            'post',
            data=data
        )
        self.dns_records.append(content['result'])
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
        if kwargs.get('proxied') is True:
            data['proxied'] = True
        else:
            data['proxied'] = False
        content = self.request(
            urllib.parse.urljoin(self.api_url, self.zone['id'] + '/dns_records/' + record['id']),
            'put',
            data=data
        )
        record.update(content['result'])
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
        cached_record_id = [i for i, rec in enumerate(self.dns_records) if rec['id'] == content['result']['id']][0]
        del self.dns_records[cached_record_id]
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

        try:
            record = self.get_record(dns_type, self.domain) \
                if len(self.domain.split('.')) == 3 \
                else self.get_record(dns_type, self.domain)
        except RecordNotFound:
            self.create_record(dns_type, self.domain, ip_address, proxied=self.proxied)
            print('Successfully created new record with IP address {new_ip}'
                  .format(new_ip=ip_address))
        else:
            if record['content'] != ip_address:
                old_ip = record['content']
                self.update_record(dns_type, self.domain, ip_address, proxied=record['proxied'])
                print('Successfully updated IP address from {old_ip} to {new_ip}'
                      .format(old_ip=old_ip, new_ip=ip_address))
            else:
                print('IP address on CloudFlare is same as your current address')
