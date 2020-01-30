# TugaRecon - funcions, write by LordNeoStark

import sys
import urllib3
import urllib.request
import webbrowser

import requests

# Colors
global G, Y, B, R, W

G = '\033[92m'  # green
Y = '\033[93m'  # yellow
B = '\033[94m'  # blue
R = '\033[91m'  # red
W = '\033[0m'   # white

def useragent():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    return user_agent


# parse host from scheme, to use for certificate transparency abuse
def parse_url(url):
    try:
        host = urllib3.util.url.parse_url(url).host
    except Exception as e:
        print('[*] Invalid domain, try again..')
        sys.exit(1)
    return host


# write subdomains to a file
def write_file(subdomains, output_file):
    # saving subdomains results to output file
    with open("results/" + output_file, 'a') as fp:
        fp.write(subdomains + '\n')
        fp.close()

def mapping_domain(target):
    try:
        urllib.request.urlretrieve(f"https://dnsdumpster.com/static/map/{target}" + ".png", f"results/{target}.png")
        webbrowser.open(f"results/{target}.png")
    except PermissionError:
        print("You dont have permission to save a file, use sudo su")


def Convert(subdomains):
    subdomains_list = list(subdomains.split(","))
    return subdomains_list



# Future implementation
'''
def merge_files(certfile, certspotterfile, host):
    aliases = {}
    with open(certfile) as f:
        for line in f:
            key, val = line.strip().split(" ")
            aliases[key] = val
    with open(certspotterfile) as f:
        for line in f:
            key, val = line.strip().split(" ")
            aliases[key] = val
    with open("merge"+host+".txt", "w") as f:
        for key, val in aliases.items():
            f.write("{} {}\n".format(key, val))
'''