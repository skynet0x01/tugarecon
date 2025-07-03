#!/usr/bin/python3
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01 2020-2025


# ----------------------------------------------------------------------------------------------------------
# import go here :)
import argparse  # parse arguments
import sys
import time
import urllib3
import requests
from progress.bar import IncrementalBar

# Import internal functions
from utils.tuga_colors import G, Y, W
from utils.tuga_banner import banner
from utils.tuga_functions import ReadFile, DeleteDuplicate, mapping_domain
from utils.tuga_dns import DNS_Record_Types, bscan_whois_look
from utils.tuga_results import main_work_subdirs
#from tuga_bruteforce import TugaBruteForce

from tuga_bruteforce import TugaBruteForce
#import asyncio

# ----------------------------------------------------------------------------------------------------------
# Import internal modules
from modules.tuga_modules import tuga_certspotter, tuga_crt, tuga_hackertarget, tuga_threatcrowd, \
                                 tuga_alienvault, tuga_threatminer, tuga_omnisint, tuga_sublist3r
from modules.tuga_modules import queries


# ----------------------------------------------------------------------------------------------------------
def data_results():
    main_work_subdirs()
    print(G + "**************************************************************\n" + W)
def override(func):
    class OverrideAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string):
            func()
            parser.exit()
    return OverrideAction


# ----------------------------------------------------------------------------------------------------------
# parse the arguments
def parse_args():
    Examples = Y + '''modules: certspotter, hackertarget, ssl, threatcrowd, alienvault, threatminer, omnisint, sublist3r\n''' + ''' [**]Examples: ''' + W + f'''
        python3 {sys.argv[0]} -d google.com                                 (Default: All modules, except bruteforce)
        python3 {sys.argv[0]} -d google.com --enum ssl                      (One or more modules)
        python3 {sys.argv[0]} -d google.com --bruteforce                    (Use first_names.txt, and next_names.txt)
        python3 {sys.argv[0]} -r                                            (View saved domains in results)

        Donations are welcome. This will help improved features, frequent updates and better overall support.
        (https://github.com/skynet0x01/tugarecon)
        '''
    parser = argparse.ArgumentParser(epilog=Examples, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser._optionals.title = "OPTIONS"
    parser.add_argument('-d', '--domain', required=True)
    parser.add_argument('-r', '--results', nargs=0, action=override(data_results), help='View saved domains results')
    parser.add_argument('--enum', nargs='*', help='<optional> Perform enumerations and network mapping')
    parser.add_argument('-b', '--bruteforce', help='Enable the bruteforce scan', action='store_true')
    parser.add_argument('-t', '--threads', metavar='', help="Number of workers to use to scan the domain. Default is 150", default=150, type=int)
    #parser.add_argument('--full', dest='full_scan', default=False, action='store_true', help='Full scan, NAMES FILE first_names_full.txt will be used to brute')
    return parser.parse_args()


# ----------------------------------------------------------------------------------------------------------
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


# ----------------------------------------------------------------------------------------------------------
def internet_on():
    url = "https://www.google.com"
    test_timeout = 2
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


# ----------------------------------------------------------------------------------------------------------
def start_bruteforce(args, target, enum, threads, bruteforce, results):
    # bruteforce fast scan
    if bruteforce:
        print("\nWait for results...! (It might take a while for the results appear) ")
        print(G + "**************************************************************\n" + W)
        subdomains_test = TugaBruteForce(options=args)
        subdomains_test.run()
        #subdomains_test = TugaBruteForceAsync(options=args)
        #asyncio.run(subdomains_test.run())
        #subdomains_test.outfile.flush()
        #subdomains_test.outfile.close()
        sys.exit()
    # END bruteforce fast scan
    
    
    # ----------------------------------------------------------------------------------------------------------
    # Modules scan: certspotter, hackertarget, ssl, threatcrowd,
    #               alienvault, threatminer, omnisint, Sublist3r
    # ----------------------------------------------------------------------------------------------------------
    try:
        # <Module required> Perform enumerations and network mapping
        supported_engines = {'certspotter': tuga_certspotter.Certspotter,
                             'ssl': tuga_crt.CRT,
                             'hackertarget': tuga_hackertarget.Hackertarget,
                             'threatcrowd': tuga_threatcrowd.Threatcrowd,
                             'alienvault': tuga_alienvault.Alienvault,
                             'threatminer': tuga_threatminer.Threatminer,
                             'omnisint': tuga_omnisint.Omnisint,
                             'sublist3r': tuga_sublist3r.Sublist3r
                            }
        chosenEnums = []

        if enum is None: # Run all modules
            start_time = time.time()
            queries(target)
            chosenEnums = [tuga_certspotter.Certspotter, tuga_crt.CRT, tuga_hackertarget.Hackertarget,
                           tuga_threatcrowd.Threatcrowd, tuga_alienvault.Alienvault, tuga_threatminer.Threatminer,
                           tuga_omnisint.Omnisint, tuga_sublist3r.Sublist3r]
            # Start super fast enumeration
            print("Running free OSINT engines...\n")
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
                    start_time = time.time()
                    # Start the enumeration
                    enums = [indicate(target) for indicate in chosenEnums]
                    DeleteDuplicate(target)
                    ReadFile(target, start_time)
        # Save map domain (png file)
        #if savemap is not False:
        #    mapping_domain(target)
    except KeyboardInterrupt:
        print(G + "**************************************************************" + W)
        print("\nTugaRecon interrupted by user\n")
        sys.exit()


# ----------------------------------------------------------------------------------------------------------
def menu_bruteforce():
    banner()
    args = parse_args()  # args = parser.parse_args()
    target = parse_url(args.domain)
    #internet_on()
    DNS_Record_Types(target)
    bscan_whois_look(target)
    enum = args.enum
    bruteforce = args.bruteforce
    threads = args.threads
    #savemap = args.savemap
    results = args.results
    start_bruteforce(args, target, enum, threads, bruteforce, results)
    


# ----------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    menu_bruteforce()
    
    
# ----------------------------------------------------------------------------------------------------------

