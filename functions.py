# TugaRecon - funcions, write by LordNeoStark
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By LordNeoStark | https://twitter.com/LordNeoStark | https://github.com/LordNeoStark

import sys
import urllib.request
import webbrowser
import urllib.error
import urllib3
import os
from pathlib import Path

# Colors

global G, Y, B, R, W

G = '\033[92m'  # green
Y = '\033[93m'  # yellow
B = '\033[94m'  # blue
R = '\033[91m'  # red
W = '\033[0m'  # white


# parse host from scheme, to use for certificate transparency abuse
def parse_url(url):
    try:
        host = urllib3.util.url.parse_url(url).host
    except Exception as e:
        print('[*] Invalid domain, try again..')
        sys.exit(1)
    return host

'''
# write subdomains to a file
def write_file(subdomains, output_file, target):
    # saving subdomains results to output file
    if not os.path.exists("results/" + target):
        os.mkdir("results/" + target)
    else:
        pass
    with open("results/" + target + "/" + output_file, 'a') as fp:
        fp.write(subdomains + '\n')
    fp.close()
    #DeleteDuplicate(target, subdomains)

    # outfile = open("results/" + target + "/merge_files.txt", "a+")
    # infile = open("results/" + target + "/" + output_file, 'r')
'''

def write_file(subdomains, output_file, target):
    # saving subdomains results to output file
    if not os.path.exists("results/" + target):
        os.mkdir("results/" + target)
    else:
        pass
    try:
        with open("results/" + target + "/" + "tmp.txt", 'a') as tmp:
            tmp.write(subdomains + '\n')
        tmp.close()
    except:
        pass


def DeleteDuplicate(output_file, target):

    content = open("results/" + target + "/" + "tmp.txt", 'r').readlines()
    content_set = set(content)
    cleandata = open("results/" + target + "/" + output_file, 'w')
    for line in content_set:
        cleandata.write(line)
    try:
        os.remove("results/" + target + "/" + "tmp.txt")
    except OSError:
        pass

    #DeleteDuplicate(target, subdomains)

def mapping_domain(target):
    try:
        try:
            urllib.request.urlretrieve(f"https://dnsdumpster.com/static/map/{target}" + ".png",
                                       f"results/{target}/{target}.png")
        except urllib.error.URLError as e:
            print("", e.reason)
        my_file = Path(f"results/{target}/{target}.png")
        if my_file.is_file():
            webbrowser.open(f"results/{target}/{target}.png")
        else:
            print(Y + "\nOops! The map file was not generated. Try again...\n" + W)
    except PermissionError:
        print("You dont have permission to save a file, use sudo su")


# Future implementation
def Convert(subdomains):
    subdomains_list = list(subdomains.split(","))
    return subdomains_list
