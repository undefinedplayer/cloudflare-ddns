# CloudFlare
### The python operator for CloudFlare API. It can sync your public ip address to dns record on CloudFlare

## Examples:
### Sync your public ip address to dns record on CloudFlare
```python
import CloudFlare from cloudflare
cf = CloudFlare(your_email, your_api_key, 'example.com')
cf.sync_dns_from_my_ip() #Successfully updated IP address from xx.xx.xx.xx to xx.xx.xx.xx
```
### RESTful dns record operation
```python
cf.get_record('A', 'sub.example.com')
```
```python
cf.create_record('A', 'sub.example.com', '202.202.202.202')
```
```python
cf.update_record('A', 'sub.example.com', '202.202.202.202')
```
```python
cf.delete_record('A', 'sub.example.com')
```
**Please note: The class will cache dns records information it gets from CloudFlare. To refresh cache, use 'refresh' method:**
```python
cf.refresh()
```
