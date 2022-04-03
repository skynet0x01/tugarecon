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
from progress.bar import IncrementalBar
#from progress.bar import Bar

# Import internal functions
from colors import G, Y, B, R, W
from functions import mapping_domain
from functions import DeleteDuplicate
from functions import ReadFile
from tuga_bruteforce import TugaBruteForce
from tuga_dns import DNS_Record_Types
from tuga_dns import bscan_whois_look

# Import internal modules
from modules import tuga_certspotter
from modules import tuga_crt
from modules import tuga_hackertarget
from modules import tuga_threatcrowd
from modules import tuga_alienvault
from modules import tuga_threatminer
from modules import tuga_omnisint
################################################################################
# Banner, Tuga or portuguese, is the same ;)
def banner():
    print(R + "              ______                  ____                      \n"
              "             /_  __/_  ______ _____ _/ __ \___  _________  ____ \n"
              "              / / / / / / __ `/ __ `/ /_/ / _ \/ ___/ __ \/ __ \                \n"
              "             / / / /_/ / /_/ / /_/ / _, _/  __/ /__/ /_/ / / / /               \n"
              "            /_/  \__,_/\__, /\__,_/_/ |_|\___/\___/\____/_/ /_/  Version 1.30               \n"
              "                      /____/                               # Coded By skynet0x01 #\n" + W)
    print(Y + "TugaRecon, tribute to Portuguese explorers reminding glorious past of this country. 2020-2022\n" + W)
################################################################################
# parse the arguments
def parse_args():
    Examples = Y + '''modules: certspotter, hackertarget, ssl, threatcrowd, alienvault, threatminer, omnisint\n''' + ''' [**]Examples: ''' + W + f'''
        python3 {sys.argv[0]} -d google.com                                 (Default: All modules, except bruteforce)
        python3 {sys.argv[0]} -d google.com --enum ssl                      (One or more modules)
        python3 {sys.argv[0]} -d google.com --enum certspotter --savemap
        python3 {sys.argv[0]} -d google.com --savemap                       (Save subdomains image map)
        python3 {sys.argv[0]} -d google.com --bruteforce                    (Use first_names.txt, and next_names.txt)
        python3 {sys.argv[0]} -d google.com -b --full                       (Use first_names_full.txt, and next_names_full.txt)

        Donations are welcome. This will help improved features, frequent updates and better overall support.
        (https://github.com/skynet0x01/tugarecon)
        '''
    parser = argparse.ArgumentParser(epilog=Examples, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser._optionals.title = "OPTIONS"
    parser.add_argument('-d', '--domain', help="[required] Domain name to enumerate it's subdomains", required=True)
    parser.add_argument('-i', '--ignore', dest='i', default=False, action='store_true', help='Ignore domains pointed to private IPs')
    parser.add_argument('-f', '--file', metavar='', dest='file', default='first_names.txt', help='A file contains new line delimited subdomains, default is first_names.txt.')
    parser.add_argument('-s', '--savemap', help='Save subdomains image map', action='store_true')
    parser.add_argument('-b', '--bruteforce', help='Enable the bruteforce scan', action='store_true')
    parser.add_argument('-t', '--threads', metavar='', help="Number of threads to use to scan the domain. Default is 200", default=200, type=int)
    parser.add_argument('--enum', nargs='*', help='<optional> Perform enumerations and network mapping')
    parser.add_argument('--full', dest='full_scan', default=False, action='store_true', help='Full scan, NAMES FILE first_names_full.txt will be used to brute')
    return parser.parse_args()
################################################################################
# parse host from scheme, to use for certificate transparency abuse, validate domain
def parse_url(url):
    try:
        host = urllib3.util.url.parse_url(url).host
        response = requests.get('http://' + host)
        if (response.status_code == 200):
            print('Target ONLINE... Lets go!')
        else:
            print('[*] Invalid domain, try again...')
    except Exception as e:
        print('[*] Network unstable... !? ')
    except KeyboardInterrupt:
        print("\nTugaRecon interrupted by user\n")
        print(G + "**************************************************************" + W)
        quit()
        #sys.exit(1)
    return host
################################################################################
def internet_on():
    url = "https://www.google.com"
    test_timeout = 1
    try:
        request = requests.get(url, timeout=test_timeout)
        print("Connection established... Wait!\n")
        time.sleep(0.5)
    except (requests.ConnectionError, requests.Timeout) as exception:
        print("No internet connection. Check the network...\n")
        exit(1)
    except KeyboardInterrupt:
        print(G + "**************************************************************" + W)
        print("\nTugaRecon interrupted by user\n")
        sys.exit()
################################################################################
def queries(target):
    print(G + "Enumerating subdomains for " + target + " \n" + W)
    time.sleep(1)
    print(R + "[-] Searching " + target + " in CertsPotter " + W)
    print(R + "[-] Searching " + target + " in SSL Certificates " + W)
    print(R + "[-] Searching "  + target + " in HackerTarget " + W)
    print(R + "[-] Searching "  + target + " in ThreatCrowd " + W)
    print(R + "[-] Searching "  + target + " in Alienvault " + W)
    print(R + "[-] Searching "  + target + " in Threatminer" + W)
    print(R + "[-] Searching "  + target + " in Omnisint\n" + W)
    time.sleep(0.5)
    return (0)
################################################################################

################################################################################
def main(target, savemap, enum, threads, bruteforce, args):
    # bruteforce fast scan
    if bruteforce:
        print("\nWait for results...!")
        print(G + "**************************************************************\n" + W)
        #d = tuga_bruteforce.TugaBruteForce(target, options=args)
        subdomains_test = TugaBruteForce(options=args)
        subdomains_test.run()
        subdomains_test.outfile.flush()
        subdomains_test.outfile.close()
        sys.exit()
    # END bruteforce fast scan
    # Modules scan
    try:
        # <Module required> Perform enumerations and network mapping
        supported_engines = {'certspotter': tuga_certspotter.Certspotter,
                             'ssl': tuga_crt.CRT,
                             'hackertarget': tuga_hackertarget.Hackertarget,
                             'threatcrowd': tuga_threatcrowd.Threatcrowd,
                             'alienvault': tuga_alienvault.Alienvault,
                             'threatminer': tuga_threatminer.Threatminer,
                             'omnisint': tuga_omnisint.Omnisint
                            }
        chosenEnums = []

        # Default modules (run all modules)
        if enum is None: # Run all modules
            start_time = time.time()
            queries(target)
            chosenEnums = [tuga_certspotter.Certspotter, tuga_crt.CRT, tuga_hackertarget.Hackertarget,
                           tuga_threatcrowd.Threatcrowd, tuga_alienvault.Alienvault, tuga_threatminer.Threatminer,
                           tuga_omnisint.Omnisint]
            # Start super fast enumeration
            print("Wait for results...! (It might take a while)")
            print(G + "**************************************************************\n" + W)
            bar = IncrementalBar('Processing', max = len(chosenEnums))
            #enums = [indicate(target) for indicate in chosenEnums]
            for indicate in chosenEnums:
                enums = indicate(target)
                bar.next()
            bar.finish()
            print(G + "\n**************************************************************\n" + W)
            DeleteDuplicate(target)
            ReadFile(target, start_time)
        else: # Perform enumerations
            for engine in enum:
                if engine.lower() in supported_engines:
                    chosenEnums.append(supported_engines[engine.lower()])
                    print("\nWait for results...!\n")
                    # Start the enumeration
                    enums = [indicate(target) for indicate in chosenEnums]
                    DeleteDuplicate(target)
                    ReadFile(target, start_time)

        # Save map domain (png file)
        if savemap is not False:
            mapping_domain(target)
    except KeyboardInterrupt:
        print(G + "**************************************************************" + W)
        print("\nTugaRecon interrupted by user\n")
        sys.exit()
################################################################################
def menu():
    banner()
    args = parse_args()  # args = parser.parse_args()
    target = parse_url(args.domain)
    internet_on()
    DNS_Record_Types(target)
    bscan_whois_look(target)
    enum = args.enum
    bruteforce = args.bruteforce
    threads = args.threads
    savemap = args.savemap
    main(target, savemap, enum, threads, bruteforce, args)
################################################################################
if __name__ == "__main__":
    menu()
################################################################################
