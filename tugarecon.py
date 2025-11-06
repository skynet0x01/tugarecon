#!/usr/bin/env python3

# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01 2020-2025

# This file is part of TugaRecon, developed by skynet0x01 in 2020-2025.
#
# Copyright (C) 2025 skynet0x01
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.


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
from tuga_bruteforce import TugaBruteForce
from tuga_network_map import tuga_map

# ----------------------------------------------------------------------------------------------------------
# Import internal modules
from modules.tuga_modules import tuga_certspotter, tuga_crt, tuga_hackertarget, tuga_threatcrowd, \
                                 tuga_alienvault, tuga_threatminer, tuga_omnisint, tuga_sublist3r, tuga_dnsdumpster
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
    Examples = (Y + '''
────────────────────────────────────────────────────────────
 Available Modules:
────────────────────────────────────────────────────────────
  • certspotter     • hackertarget   • ssl           • threatcrowd
  • alienvault      • threatminer    • omnisint      • sublist3r

────────────────────────────────────────────────────────────
 Examples of Usage:
────────────────────────────────────────────────────────────
  ▶ Enumerate all modules (except bruteforce):
      python3 {0} -d google.com

  ▶ Use a specific module (e.g., ssl):
      python3 {0} -d google.com --enum ssl

  ▶ Bruteforce subdomains using wordlists:
      python3 {0} -d google.com --bruteforce
      python3 {0} -d google.com -b

  ▶ View saved results:
      python3 {0} -r

  ▶ Generate network graph (with ASN clusters):
      python3 {0} -d google.com -m

────────────────────────────────────────────────────────────
 Donations are welcome ♥
 Help improve features, updates, and support:
 → https://github.com/skynet0x01/tugarecon
────────────────────────────────────────────────────────────
'''.format(sys.argv[0]) + W)

    parser = argparse.ArgumentParser(
        epilog=Examples,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser._optionals.title = "OPTIONS"

    parser.add_argument(
        '-d', '--domain', required=True,
        help='Domain to enumerate (e.g., example.com)'
    )

    parser.add_argument(
        '-r', '--results', nargs=0,
        action=override(data_results),
        help='Show previously saved results for domains'
    )

    parser.add_argument(
        '-e', '--enum', nargs='*',
        help='[Optional] Select specific modules for enumeration (e.g., ssl, certspotter)'
    )

    parser.add_argument(
        '-b', '--bruteforce', action='store_true',
        help='Enable brute force subdomain discovery using wordlists'
    )

    parser.add_argument(
        '-t', '--threads', metavar='', type=int, default=250,
        help='Number of concurrent threads to use (default: 250)'
    )

    parser.add_argument(
        '-m', '--map', action='store_true',
        help='Generate network map with ASN clusters and grouped device icons'
    )
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
def start_tugarecon(args, target, enum, threads, bruteforce, savemap, results):
    # bruteforce fast scan


    if bruteforce:
        print("\nWait for results...! (It might take a while for the results appear) ")
        print(G + "**************************************************************\n" + W)
        subdomains_test = TugaBruteForce(options=args)
        subdomains_test.run()
        sys.exit()
    # END bruteforce fast scan

    # ----------------------------------------------------------------------------------------------------------
    # Save map domain (png file)
    if savemap is not False:
        tuga_map(target)
        sys.exit()
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
                             'sublist3r': tuga_sublist3r.Sublist3r,
                             'dnsdumpster': tuga_dnsdumpster.DNSDUMPSTER
                            }
        chosenEnums = []

        if enum is None: # Run all modules
            start_time = time.time()
            queries(target)

            chosenEnums = [tuga_certspotter.Certspotter, tuga_crt.CRT, tuga_hackertarget.Hackertarget,
                           tuga_threatcrowd.Threatcrowd, tuga_alienvault.Alienvault, tuga_threatminer.Threatminer,
                           tuga_omnisint.Omnisint, tuga_sublist3r.Sublist3r, tuga_dnsdumpster.DNSDUMPSTER]

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

        # # Save map domain (png file)
        # if savemap is not False:
        #     tuga_map(target)

    except KeyboardInterrupt:
        print(G + "**************************************************************" + W)
        print("\nTugaRecon interrupted by user\n")
        sys.exit()


# ----------------------------------------------------------------------------------------------------------
def menu_tugarecon():
    banner()
    args = parse_args()  # args = parser.parse_args()
    target = parse_url(args.domain)
    DNS_Record_Types(target)
    bscan_whois_look(target)
    enum = args.enum
    bruteforce = args.bruteforce
    threads = args.threads
    results = args.results
    savemap = args.map
    start_tugarecon(args, target, enum, threads, bruteforce, savemap, results)



# ----------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    menu_tugarecon()

# ----------------------------------------------------------------------------------------------------------

