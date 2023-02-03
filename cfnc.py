#!/usr/local/bin/python3
import os
import sys
import requests
import yaml

# read credentials from config file
try:
    credentials_file = open('credentials.yaml', 'r')
    credentials = yaml.safe_load(credentials_file)
except (FileNotFoundError) as error:
    print('Error: No credentials.yaml file found')
    sys.exit(1)

CF_ACCOUNTS = credentials['CF_ACCOUNTS']
NC_API_USER = credentials['NC_API_USER']
NC_API_KEY = credentials['NC_API_KEY']

# Cloudflare API URL
CF_API_URL = "https://api.cloudflare.com/client/v4"

# Namecheap API URL
NC_API_URL = "https://api.namecheap.com/xml.response"

def list_zones(cf_account):
    url = CF_API_URL + "/zones"
    headers = {
        'X-Auth-Account': cf_account["account_id"],
        'X-Auth-Email': cf_account["email"],
        'X-Auth-Key': cf_account["api_key"],
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    if result['success'] == True:
        print('Zones: ')
        for zone in result['result']:
            print(zone['name'])
    else:
        print('Error fetching zones.')

def add_zone(domain, cf_account):
    url = CF_API_URL + "/zones"
    data = {
        "name": domain,
        "jump_start": True
    }
    headers = {
        'X-Auth-Account': cf_account["account_id"],
        'X-Auth-Email': cf_account["email"],
        'X-Auth-Key': cf_account["api_key"],
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=data, headers=headers)
    if result['success'] == True:
        print('Zone added.')
        print('Nameservers: ')
        for ns in result['result']['name_servers']:
            if ns != result['result']['name_servers'][-1]:
                print(ns, end=",")
            else:
                print(ns)
    else:
        print('Error adding zone.')


# Add forcing https for the Cloudflare API Script
def enforce_https(domain, cf_account):
    zone_id = get_zone_id(domain, cf_account)
    url = CF_API_URL + "/zones/" + zone_id + "/settings/ssl"
    data = {
        'value': 'full'
    }
    headers = {
        'X-Auth-Account': cf_account["account_id"],
        'X-Auth-Email': cf_account["email"],
        'X-Auth-Key': cf_account["api_key"],
        'Content-Type': 'application/json'
    }
    response = requests.patch(url, json=data, headers=headers)
    result = response.json()
    if result['success'] == True:
        print('HTTPS enforced.')
    else:
        print('Error enforcing HTTPS.')

def add_record(domain, name, type, content, cf_account):
    zone_id = get_zone_id(domain, cf_account)
    url = CF_API_URL + "/zones/" + zone_id + "/dns_records"
    data = {
        "type": type,
        "name": name,
        "content": content,
        "ttl": 1
    }
    headers = {
        'X-Auth-Account': cf_account["account_id"],
        'X-Auth-Email': cf_account["email"],
        'X-Auth-Key': cf_account["api_key"],
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=data, headers=headers)
    result = response.json()
    if result['success'] == True:
        print('Record added.')
    else:
        print('Error adding record.')

def remove_record(domain, cf_account):
    zone_id = get_zone_id(domain, cf_account)
    url = CF_API_URL + "/zones/" + zone_id + "/dns_records"
    headers = {
        'X-Auth-Account': cf_account["account_id"],
        'X-Auth-Email': cf_account["email"],
        'X-Auth-Key': cf_account["api_key"],
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    if result['success'] == True:
        record_list = result['result']
        if len(record_list) > 0:
            print("Please select the record you wish to delete by its number:")
            for i in range(len(record_list)):
                print("{0}: {1} {2}".format(i+1, record_list[i]["name"], record_list[i]["type"]))
            record_id = record_list[int(input())-1]["id"]
            if record_id:
                url = CF_API_URL + "/zones/" + zone_id + "/dns_records/" + record_id
                response = requests.delete(url, headers=headers)
                result = response.json()
                if result['success'] == True:
                    print('Record deleted.')
                else:
                    print('Error deleting record.')
            else:
                print('Record not found.')
        else:
            print('No records found.')
    else:
        print('Error removing record.')

def update_nameservers(domain, nameservers):
    url = NC_API_URL
    data = {
        "ApiUser": NC_API_USER,
        "ApiKey": NC_API_KEY,
        "UserName": NC_API_USER,
        "Command": "namecheap.domains.dns.setHosts",
        "ClientIp": "0.0.0.0",
        "SLD": domain.split('.')[0],
        "TLD": domain.split('.')[1]
    }
    for i, ns in enumerate(nameservers):
        data['HostName' + str(i+1)] = ns
    response = requests.post(url, data=data)
    result = response.text
    if '<ErrCount>0</ErrCount>' in result:
        print('Nameservers updated.')
    else:
        print('Error updating nameservers.')

def get_zone_id(domain, cf_account):
    url = CF_API_URL + "/zones?name=" + domain
    headers = {
        'X-Auth-Account': cf_account["account_id"],
        'X-Auth-Email': cf_account["email"],
        'X-Auth-Key': cf_account["api_key"],
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    if result['success'] == False:
        print('Error fetching zone.')
    zone_id = result['result'][0]['id']
    return zone_id

def show_choices(cf_account):
    print("\nChoose an action:")
    print("1. List zones")
    print("2. Add zone")
    print("3. Add record")
    print("4. Remove record")
    print("5. Enforce HTTPS")
    print("6. Update nameservers of domain\n")

# =====================================================================================================================

# Ask for the cloudflare credentials to use
print("\nChoose the Cloudflare account to use:")
for i, cf_account in enumerate(CF_ACCOUNTS):
    print(str(i+1) + ". " + cf_account["email"])

cf_choice = int(input('> '))
cf_account = CF_ACCOUNTS[cf_choice-1]

try:
    while True:
        show_choices(cf_account)
        choice = input('> ')
        if choice == '1':
            list_zones(cf_account)
        if choice == '2':
            domain = input('Enter domain: ')
            add_zone(domain, cf_account)
        elif choice == '3':
            domain = input('Enter domain: ')
            name = input('Enter record name: ')
            type = input('Enter record type: ')
            content = input('Enter record content: ')
            add_record(domain, name, type, content, cf_account)
        elif choice == '4':
            domain = input('Enter domain: ')
            remove_record(domain, cf_account)
        if choice == '5':
            domain = input('Enter domain: ')
            enforce_https(domain, cf_account)
        elif choice == '6':
            domain = input('Enter domain: ')
            nameservers = input('Enter nameservers (separate by comma): ').split(',')
            update_nameservers(domain, nameservers)
except KeyboardInterrupt:
    sys.exit(0)
