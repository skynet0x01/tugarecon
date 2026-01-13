#!/usr/bin/env python3

# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01 2020-2026

# This file is part of TugaRecon, developed by skynet0x01 in 2020-2026.
#
# Copyright (C) 2026 skynet0x01
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
import os
import argparse  # parse arguments
import sys
import time
import urllib3
import requests
import json

from datetime import datetime
from progress.bar import IncrementalBar

# Import internal functions
from utils.tuga_colors import G, Y, W
from utils.tuga_banner import banner
from utils.tuga_save import ReadFile, DeleteDuplicate
from utils.tuga_dns import DNS_Record_Types, bscan_whois_look
from utils.tuga_results import main_work_subdirs
from tuga_bruteforce import TugaBruteForce
from tuga_network_map import tuga_map

# Import internal modules
from modules.tuga_modules import tuga_certspotter, tuga_crt, tuga_hackertarget, tuga_threatcrowd, \
                                 tuga_alienvault, tuga_threatminer, tuga_omnisint, tuga_sublist3r, tuga_dnsdumpster
from modules.tuga_modules import queries

from modules.ia_subdomain.ia_generator import IASubdomainGenerator
from modules.ia_subdomain.ia_wordlist import enrich_wordlist_from_ia
from modules.ia_subdomain.bruteforce_hint import generate_hints

from modules.intelligence.snapshot import load_previous_snapshot, build_snapshot, save_snapshot
from utils.temporal_view import print_top_temporal
from utils.temporal_analysis import analyze_temporal_state


# ----------------------------------------------------------------------------------------------------------
def run_temporal_intelligence(scan_dir):
    semantic_file = os.path.join(scan_dir, "semantic_results.json")
    if not os.path.isfile(semantic_file):
        return

    with open(semantic_file, "r") as f:
        classified_results = json.load(f)

    previous_snapshot = load_previous_snapshot(scan_dir)
    snapshot = build_snapshot(classified_results, previous_snapshot)
    save_snapshot(scan_dir, snapshot)

    temporal_states = analyze_temporal_state(snapshot, previous_snapshot)

    temporal_rank = []

    for state, subs in temporal_states.items():
        score_map = {
            "ESCALATED": 4,
            "NEW": 3,
            "STABLE": 2,
            "FLAPPING": 1
        }

        for sub in subs:
            temporal_rank.append({
                "subdomain": sub,
                "state": state,
                "score": score_map.get(state, 0)
            })

    # temporal_rank = []
    # for state, subs in temporal_states.items():
    #     for sub in subs:
    #         temporal_rank.append({
    #             "subdomain": sub,
    #             "state": state,
    #             "score": (
    #                 4 if state == "ESCALATED" else
    #                 3 if state == "NEW" else
    #                 2 if state == "STABLE" else
    #                 1 if state == "FLAPPING" else
    #                 0
    #             )
    #         })

    temporal_rank.sort(key=lambda x: x["score"], reverse=True)
    print_top_temporal(temporal_rank, limit=20)

    print("[IA] Snapshot saved (temporal memory updated)")


# ----------------------------------------------------------------------------------------------------------
def run_ia_training(target):
    base_dir = f"results/{target}"
    if not os.path.isdir(base_dir):
        return

    dates = []
    for d in os.listdir(base_dir):
        try:
            datetime.strptime(d, "%Y-%m-%d")
            dates.append(d)
        except ValueError:
            pass

    if not dates:
        return

    latest_date = sorted(dates)[-1]
    subdomains_file = os.path.join(base_dir, latest_date, "subdomains.txt")
    if not os.path.isfile(subdomains_file):
        return

    with open(subdomains_file) as f:
        found_subdomains = [l.strip() for l in f if l.strip()]

    if len(found_subdomains) < 2:
        print("[IA] Not enough data to generate patterns")
        return

    print(f"[IA] Training with {len(found_subdomains)} subdomains")

    ia = IASubdomainGenerator(limit=1000)
    ia_candidates = ia.generate(found_subdomains)
    enrich_wordlist_from_ia(ia_candidates)


# ----------------------------------------------------------------------------------------------------------
def data_results():
    main_work_subdirs()
    print(G + "────────────────────────────────────────────────────────────" + W)
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
        print(G + "────────────────────────────────────────────────────────────" + W)
        quit()
        #sys.exit(1)
    return host


# ----------------------------------------------------------------------------------------------------------
def start_tugarecon(args, target, enum, threads, bruteforce, savemap, results):

    # ───────── BRUTEFORCE ─────────
    if bruteforce:
        print("\nWait for results...! (It might take a while)")
        print(G + "────────────────────────────────────────────────────────────\n" + W)

        if hasattr(args, "semantic_results") and args.semantic_results:
            args.semantic_hints = generate_hints(args.semantic_results)
            print(f"[IA] Generated {len(args.semantic_hints)} semantic hints")
        else:
            args.semantic_hints = []

        TugaBruteForce(options=args).run()
        sys.exit()

    # ───────── MAP ─────────
    if savemap:
        tuga_map(target)
        sys.exit()

    # ───────── ENUMERATION ─────────
    try:
        supported_engines = {
            'certspotter': tuga_certspotter.Certspotter,
            'ssl': tuga_crt.CRT,
            'hackertarget': tuga_hackertarget.Hackertarget,
            'threatcrowd': tuga_threatcrowd.Threatcrowd,
            'alienvault': tuga_alienvault.Alienvault,
            'threatminer': tuga_threatminer.Threatminer,
            'omnisint': tuga_omnisint.Omnisint,
            'sublist3r': tuga_sublist3r.Sublist3r,
            'dnsdumpster': tuga_dnsdumpster.DNSDUMPSTER
        }

        chosenEnums = (
            list(supported_engines.values())
            if enum is None
            else [supported_engines[e.lower()] for e in enum if e.lower() in supported_engines]
        )

        start_time = time.time()
        queries(target)

        print("Running free OSINT engines...\n")
        bar = IncrementalBar('Processing', max=len(chosenEnums))

        for engine in chosenEnums:
            engine(target)
            bar.next()

        bar.finish()
        print(G + "\n────────────────────────────────────────────────────────────\n" + W)

        DeleteDuplicate(target)
        ReadFile(target, start_time)

        # ───────── INTELLIGENCE ─────────
        scan_dir = f"results/{target}/{datetime.now().date()}"

        try:
            run_temporal_intelligence(scan_dir)
        except Exception as e:
            print(f"[IA] Snapshot failed: {e}")

        run_ia_training(target)

    except KeyboardInterrupt:
        print(G + "────────────────────────────────────────────────────────────" + W)
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