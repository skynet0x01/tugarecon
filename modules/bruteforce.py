import argparse
import sys

import requests
import urllib3


def parse_args():
    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython3 ' + sys.argv[0] + " -d google.com")
    parser._optionals.title = "OPTIONS"
    parser.add_argument('-d', '--domain', type=str, help="Domain name to enumerate it's subdomains", required=True)
    return parser.parse_args()


def parse_url(url):
    try:
        host = urllib3.util.url.parse_url(url).host
    except Exception as e:
        print('[*] Invalid domain, try again..')
        sys.exit(1)
    return host


args = parse_args()
target = parse_url(args.domain)

# the domain to scan for subdomains
# domain = "sapo.pt"

# read all subdomains in file
file = open("../../subdomains.txt")
# read all content
content = file.read()
# split by new lines
subdomains = content.splitlines()

for subdomain in subdomains:
    # construct the url
    url = f"http://{subdomain}.{target}"
    try:
        # if this raises an ERROR, that means the subdomain does not exist
        requests.get(url)
    except requests.ConnectionError:
        # if the subdomain does not exist, just pass, print nothing
        # pass
        print("ERROR: ", url)
    else:
        print("[+] Discovered subdomain:", url)
