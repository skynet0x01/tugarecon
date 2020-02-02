#!/usr/bin/python3

# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By LordNeoStark | https://twitter.com/LordNeoStark | https://github.com/LordNeoStark

# import go here :)

import argparse  # parse arguments
import sys
import time

import urllib3

# Import internal functions
from functions import R, W, Y
from functions import mapping_domain

# Import internal modules
from modules import certspotter
from modules import crt
from modules import hackertarget
from modules import threatcrowd
from modules import virustotal
from modules import tugamod  # bruteforce scan subdomains
from modules import scan


# import thread
# import threading


# Banner, Tuga or portuguese, is the same ;)
def banner():
    print("        \n"
          "             ______                  ____                      \n"
          "            /_  __/_  ______ _____ _/ __ \___  _________  ____ \n"
          "             / / / / / / __ `/ __ `/ /_/ / _ \/ ___/ __ \/ __ \                \n"
          "            / / / /_/ / /_/ / /_/ / _, _/  __/ /__/ /_/ / / / /               \n"
          "           /_/  \__,_/\__, /\__,_/_/ |_|\___/\___/\____/_/ /_/  V: 0.25b               \n"
          "                     /____/                                    \n"
          "\n"
          "                        # Coded By LordNeoStark #\n"
          "    ")


# parser error
def parser_error(errmsg):
    print("Usage: python3 " + sys.argv[0] + " [Options] use -h for help")
    print("Error: " + errmsg)
    sys.exit(1)


# parse the arguments
def parse_args():
    example_text = f'''Examples:
        python3 {sys.argv[0]} -d google.com
        python3 {sys.argv[0]} -d google.com --enum ssl
        python3 {sys.argv[0]} -d google.com --enum certspotter --savemap
        python3 {sys.argv[0]} -d google.com -o google.txt
        python3 {sys.argv[0]} -d google.com -savemap
        \nmodules: certspotter, hackertarget, virustotal, threatcrowd, ssl\n
        '''
    parser = argparse.ArgumentParser(epilog=example_text, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.error = parser_error
    parser._optionals.title = "OPTIONS"
    parser.add_argument('-d', '--domain', type=str, help="Domain name to enumerate it's subdomains", required=True)
    parser.add_argument('-p', '--ports', help='Scan the found subdomains against specified tcp ports')
    parser.add_argument('-o', '--output', help='Save the results to text file')
    parser.add_argument('-s', '--savemap', help='Save image map domain', action='store_true')
    parser.add_argument('-b', '--bruteforce', help='Enable the bruteforce module', action='store_true')
    parser.add_argument("-t", "--threads", help="Number of threads to use to scan the domain. Default is 10",
                        default=10, type=int)
    parser.add_argument("-l", "--wordlist",
                        help="File that contains all subdomains to scan, line by line. Default is subdomains.txt",
                        default="wordlist/subdomains.txt")
    parser.add_argument('--enum', nargs='*', help='<Module required> Perform enumerations and network mapping')
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
    print(Y + "TugaRecon, tribute to Portuguese explorers reminding glorious past of this country\n" + W)
    print(R + "Querying SSL Certificates for " + target + " subdomains" + W)
    print(R + "Querying CertsPotter for " + target + " subdomains" + W)
    print(R + "Querying Virustotal for " + target + " subdomains" + W)
    print(R + "Querying ThreatCrowd for " + target + " subdomains\n" + W)
    time.sleep(2)


def main(target, output, port, savemap, enum, wordlist, threads, bruteforce):

    # bruteforce scan
    if bruteforce:
        sublist= open(wordlist).read().splitlines()
        scan.main(target, threads, sublist)
        sys.exit()
    # search_list = set()

    try:

        # <Module required> Perform enumerations and network mapping

        supported_engines = {'certspotter': certspotter.Certspotter,
                             'hackertarget': hackertarget.Hackertarget,
                             'virustotal': virustotal.Virustotal,
                             'threatcrowd': threatcrowd.Threatcrowd,
                             'ssl': crt.CRT
                             }
        chosenEnums = []

        if enum is None:
            queries(target)
            chosenEnums = [certspotter.Certspotter, hackertarget.Hackertarget, virustotal.Virustotal,
                           threatcrowd.Threatcrowd, crt.CRT]
            # Start the enumeration

            enums = [indicate(target, output) for indicate in chosenEnums]

        else:

            for engine in enum:
                if engine.lower() in supported_engines:
                    chosenEnums.append(supported_engines[engine.lower()])
                    # Start the enumeration

                    enums = [indicate(target, output) for indicate in chosenEnums]

        # Save map domain

        if savemap is not False:
            mapping_domain(target)
    except KeyboardInterrupt:
        print("\nTugaRecon interrupted by user\n")
        sys.exit()


def menu():
    banner()

    args = parse_args()  # args = parser.parse_args()
    target = parse_url(args.domain)
    output = args.output
    port = args.ports
    savemap = args.savemap
    enum = args.enum
    wordlist = args.wordlist
    threads = args.threads
    bruteforce = args.bruteforce

    main(target, output, port, savemap, enum, wordlist, threads, bruteforce)


if __name__ == "__main__":
    menu()

#####################################################################################################
