#!/usr/bin/python3
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01
################################################################################
# import go here :)
import argparse  # parse arguments
import sys
import time
import urllib3
import requests
# Import internal functions
from functions import R, W, Y, G
from functions import mapping_domain
from tuga_bruteforce import TugaBruteForce
from tuga_dns import bscan_dns_queries
from tuga_dns import bscan_whois_look
# Import internal modules
from modules import tuga_certspotter
from modules import tuga_crt
from modules import tuga_hackertarget
from modules import tuga_threatcrowd
################################################################################
# Banner, Tuga or portuguese, is the same ;)
def banner():
    print(R + "        \n"
              "             ______                  ____                      \n"
              "            /_  __/_  ______ _____ _/ __ \___  _________  ____ \n"
              "             / / / / / / __ `/ __ `/ /_/ / _ \/ ___/ __ \/ __ \                \n"
              "            / / / /_/ / /_/ / /_/ / _, _/  __/ /__/ /_/ / / / /               \n"
              "           /_/  \__,_/\__, /\__,_/_/ |_|\___/\___/\____/_/ /_/  V: 1.0               \n"
              "                     /____/                                    \n"
              "\n"
              "                        # Coded By skynet0x01 #\n"
              "    " + W)
    print(Y + "TugaRecon, tribute to Portuguese explorers reminding glorious past of this country\n" + W)
################################################################################
# parse the arguments
def parse_args():
    Examples = f'''\nmodules: certspotter, hackertarget, ssl, threatcrowd\n
        Examples:
        python3 {sys.argv[0]} -d google.com
        python3 {sys.argv[0]} -d google.com --enum ssl
        python3 {sys.argv[0]} -d google.com --enum certspotter --savemap
        python3 {sys.argv[0]} -d google.com -o google.txt
        python3 {sys.argv[0]} -d google.com --savemap
        python3 {sys.argv[0]} -d google.com --bruteforce
        python3 {sys.argv[0]} -d google.com -b --full

        Donations are welcome. This will help improved features, frequent updates and better overall support.
        (https://github.com/skynet0x01/tugarecon)
        '''
    parser = argparse.ArgumentParser(epilog=Examples, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser._optionals.title = "OPTIONS"
    parser.add_argument('-d', '--domain', type=str, metavar='', help="[required] Domain name to enumerate it's subdomains", required=True)
    parser.add_argument('-o', '--output', metavar='', help='Save the results to txt file')
    parser.add_argument('-i', '--ignore', dest='i', default=False, action='store_true', help='Ignore domains pointed to private IPs')
    parser.add_argument('-f', '--file', metavar='', dest='file', default='first_names.txt', help='A file contains new line delimited subdomains, default is first_names.txt.')
    parser.add_argument('-s', '--savemap', help='Save subdomains image map', action='store_true')
    parser.add_argument('-b', '--bruteforce', help='Enable the bruteforce scan', action='store_true')
    parser.add_argument('-t', '--threads', metavar='', help="Number of threads to use to scan the domain. Default is 200", default=200, type=int)
    parser.add_argument('--enum', nargs='*', help='<optional> Perform enumerations and network mapping')
    parser.add_argument('--full', dest='full_scan', default=False, action='store_true', help='Full scan, NAMES FILE first_names_full.txt will be used to brute')
    return parser.parse_args()
################################################################################
# parse host from scheme, to use for certificate transparency abuse
def parse_url(url):
    try:
        host = urllib3.util.url.parse_url(url).host
    except Exception as e:
        print('[*] Invalid domain, try again...')
        sys.exit(1)
    return host
################################################################################
def queries(target):
    print(G + "Enumerating subdomains for " + target + " \n" + W)
    time.sleep(0.1)
    print(R + "Searching in CertsPotter in " + target + " " + W)
    time.sleep(0.1)
    print(R + "Searching in SSL Certificates in " + target + " " + W)
    time.sleep(0.1)
    print(R + "Searching in HackerTarget in " + target + " " + W)
    time.sleep(0.1)
    print(R + "Searching in ThreatCrowd in " + target + " \n" + W)
    time.sleep(1)
################################################################################
def internet_on():
    url = "https://www.google.com"
    test_timeout = 1
    try:
        request = requests.get(url, timeout=test_timeout)
        print("Connection established... Wait!\n")
        time.sleep(1)
    except (requests.ConnectionError, requests.Timeout) as exception:
        print("No internet connection. Check the network...\n")
        exit(1)
################################################################################
def main(target, output, savemap, enum, threads, bruteforce, args):
    # bruteforce fast scan
    if bruteforce:
        #d = tuga_bruteforce.TugaBruteForce(target, options=args)
        d = TugaBruteForce(target, options=args)
        d.run()
        d.outfile.flush()
        d.outfile.close()
        sys.exit()
    try:
        # <Module required> Perform enumerations and network mapping
        supported_engines = {'certspotter': tuga_certspotter.Certspotter,
                             'ssl': tuga_crt.CRT,
                             'hackertarget': tuga_hackertarget.Hackertarget,
                             'threatcrowd': tuga_threatcrowd.Threatcrowd
                            }
        chosenEnums = []
        # Default modules (run all modules)
        if enum is None:
            queries(target)
            chosenEnums = [tuga_certspotter.Certspotter, tuga_crt.CRT, tuga_hackertarget.Hackertarget, tuga_threatcrowd.Threatcrowd]
            # Start super fast enumeration
            enums = [indicate(target, output) for indicate in chosenEnums]
        else:
            for engine in enum:
                if engine.lower() in supported_engines:
                    chosenEnums.append(supported_engines[engine.lower()])
                    # Start the enumeration
                    enums = [indicate(target, output) for indicate in chosenEnums]
        # Save map domain (png file)
        if savemap is not False:
            mapping_domain(target)
    except KeyboardInterrupt:
        print("\nTugaRecon interrupted by user\n")
        sys.exit()
################################################################################
def menu():
    banner()
    args = parse_args()  # args = parser.parse_args()
    target = parse_url(args.domain)
    enum = args.enum
    bruteforce = args.bruteforce
    threads = args.threads
    output = args.output
    savemap = args.savemap
    internet_on()
    bscan_dns_queries(target)
    bscan_whois_look(target)
    main(target, output, savemap, enum, threads, bruteforce, args)
################################################################################
if __name__ == "__main__":
    menu()
################################################################################
