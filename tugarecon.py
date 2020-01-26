#!/usr/bin/python3

# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By LordNeoStark

# import go here :)

import argparse  # parse arguments
import sys
import time

import urllib3

# Import internal modules
from modules import certspotter
from modules import crt
from modules import virustotal
from modules import threatcrowd
from functions import R, W


# Banner, Tuga or portuguese, is the same ;)
def banner():
    print("        \n"
          "             ______                  ____                      \n"
          "            /_  __/_  ______ _____ _/ __ \___  _________  ____ \n"
          "             / / / / / / __ `/ __ `/ /_/ / _ \/ ___/ __ \/ __ \                \n"
          "            / / / /_/ / /_/ / /_/ / _, _/  __/ /__/ /_/ / / / /               \n"
          "           /_/  \__,_/\__, /\__,_/_/ |_|\___/\___/\____/_/ /_/  V: 0.11b               \n"
          "                     /____/                                    \n"
          "\n"
          "                        # Coded By LordNeoStark #\n"
          "    ")


# parser error
def parser_error(errmsg):
    print("Usage: python3 " + sys.argv[0] + " [Options] use -h for help")
    print("Error: " + errmsg)
    sys.exit()


# parse the arguments
def parse_args():
    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython3 ' + sys.argv[0] + " -d google.com")
    parser.error = parser_error
    parser._optionals.title = "OPTIONS"
    parser.add_argument('-d', '--domain', type=str, help="Domain name to enumerate it's subdomains", required=True)
    parser.add_argument('-b', '--bruteforce', help='Enable the subbrute bruteforce module', nargs='?', default=False)
    parser.add_argument('-p', '--ports', help='Scan the found subdomains against specified tcp ports')
    parser.add_argument('-o', '--output', help='Save the results to text file')
    return parser.parse_args()


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

def queries(target):
    print(R + "Querying SSL Certificates for " + target + " subdomains" + W)
    print(R + "Querying CertsPotter for " + target + " subdomains" + W)
    print(R + "Querying Virustotal for " + target + " subdomains" + W)
    print(R + "Querying ThreatCrowd for " + target + " subdomains\n" + W)
    time.sleep(2)

def main():
    banner()

    args = parse_args()  # args = parser.parse_args()
    target = parse_url(args.domain)
    output = args.output

    # default search
    if target:
        queries(target)
        crt.CRT(target, output)
        input("\nPress Enter to continue...")
        certspotter.Certspotter(target, output)
        input("\nPress Enter to continue...")
        virustotal.Virustotal(target, output)
        input("|nPress Enter to continue...")
        threatcrowd.Threatcrowd(target, output)

if __name__ == "__main__":
    main()

#####################################################################################################
