# --------------------------------------------------------------------------------------------------
# TugaRecon – CLI Orchestrator (Refactored)
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

"""
This file is the main orchestration layer of TugaRecon.
Responsibilities:
 - CLI parsing
 - High-level execution flow
 - Scan context lifecycle

It deliberately avoids implementation details of OSINT, IA, Bruteforce or Mapping modules.
"""

import os
import sys
import time
import argparse
import logging
import json

from datetime import datetime
from dataclasses import dataclass, field

from utils.tuga_banner import banner
from utils.tuga_colors import G, W
from utils.tuga_dns import bscan_whois_look
from utils.tuga_results import main_work_subdirs
from utils.tuga_save import ReadFile, DeleteDuplicate
from modules.IA.trainer import run_ia_training

# --------------------------------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
log = logging.getLogger(" tugarecon")


# --------------------------------------------------------------------------------------------------
# Scan Context
# --------------------------------------------------------------------------------------------------
@dataclass
class ScanContext:
    target: str
    enum: list | None
    bruteforce: bool
    threads: int
    savemap: bool
    args: argparse.Namespace

    start_time: float = field(default_factory=time.time)
    semantic_hints: list = field(default_factory=list)

    @property
    def scan_dir(self) -> str:
        return f"results/{self.target}/{datetime.now().date()}"


# --------------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-d', '--domain', required=True, help='Target domain')
    parser.add_argument('-e', '--enum', nargs='*', help='Select OSINT modules')
    parser.add_argument('-b', '--bruteforce', action='store_true', help='Enable bruteforce')
    parser.add_argument('-t', '--threads', type=int, default=250)
    parser.add_argument('-m', '--map', action='store_true', help='Generate network map')
    parser.add_argument('--debug', action='store_true', help='Debug mode')

    return parser.parse_args()


# --------------------------------------------------------------------------------------------------
# Pipelines
# --------------------------------------------------------------------------------------------------
def run_bruteforce(ctx: ScanContext) -> None:
    log.info(" Running brute force module")

    from modules.Brute_Force.tuga_bruteforce import TugaBruteForce
    from modules.IA.bruteforce_hint import generate_hints

    if hasattr(ctx.args, "semantic_results") and ctx.args.semantic_results:
        ctx.semantic_hints = generate_hints(ctx.args.semantic_results)
        log.info(f" Generated {len(ctx.semantic_hints)} IA hints")

    options = {
        "target": ctx.target,
        "threads": ctx.threads,
        "semantic_hints": ctx.semantic_hints,
    }

    TugaBruteForce(options=options).run()


def run_map(ctx: ScanContext) -> None:
    log.info(" Generating network map")
    from modules.Map.tuga_network_map import tuga_map
    tuga_map(ctx.target)


def run_enumeration(ctx: ScanContext) -> None:
    log.info(" Starting OSINT enumeration")

    from progress.bar import IncrementalBar
    from modules.OSINT.tuga_modules import queries
    from modules.OSINT import (
        tuga_sublist3r,
        tuga_threatcrowd,
        tuga_crt,
        tuga_threatminer,
        tuga_certspotter,
        tuga_dnsdumpster,
        tuga_alienvault,
        tuga_hackertarget,
        tuga_omnisint,
    )

    engines = {
        'certspotter': tuga_certspotter.Certspotter,
        'ssl': tuga_crt.CRT,
        'hackertarget': tuga_hackertarget.Hackertarget,
        'threatcrowd': tuga_threatcrowd.Threatcrowd,
        'alienvault': tuga_alienvault.Alienvault,
        'threatminer': tuga_threatminer.Threatminer,
        'omnisint': tuga_omnisint.Omnisint,
        'sublist3r': tuga_sublist3r.Sublist3r,
        'dnsdumpster': tuga_dnsdumpster.DNSDUMPSTER,
    }

    selected = engines.values() if ctx.enum is None else [
        engines[e] for e in ctx.enum if e in engines
    ]

    queries(ctx.target)
    bar = IncrementalBar('OSINT', max=len(selected))

    for engine in selected:
        engine(ctx.target)
        bar.next()

    bar.finish()

    DeleteDuplicate(ctx.target)
    ReadFile(ctx.target, ctx.start_time)

    # IA learning from OSINT results
    run_ia_training(ctx.target)

def run_intelligence(ctx: ScanContext) -> None:
    log.info(" Running temporal intelligence")

    from utils.temporal_analysis import analyze_temporal_state
    from utils.temporal_score import compute_temporal_score
    from utils.temporal_view import print_top_temporal
    from modules.Intelligence.snapshot import load_previous_snapshot, build_snapshot, save_snapshot
    from modules.Intelligence.decision_engine import decide_action
    from modules.Intelligence.reaction_engine import react

    semantic_file = os.path.join(ctx.scan_dir, "semantic_results.json")
    if not os.path.isfile(semantic_file):
        log.warning("Semantic results not found, skipping IA")
        return

    previous = load_previous_snapshot(ctx.scan_dir)

    with open(semantic_file, "r") as f:
        results = json.load(f)

    snapshot = build_snapshot(results, previous)
    save_snapshot(ctx.scan_dir, snapshot)

    states = analyze_temporal_state(snapshot, previous)
    ranking = []

    for state, subs in states.items():
        for sub in subs:
            data = snapshot['subdomains'].get(sub, {})
            score = compute_temporal_score(data, state)
            action = decide_action(sub, data.get('impact', 0), state, score)
            ranking.append((score, sub, state, action))

    ranking.sort(reverse=True)

    # ───────── Check if there is any actionable item ─────────
    has_actionable = any(action != "IGNORE" for _, _, _, action in ranking)

    # ───────── Temporal Risk View Output ─────────
    print("\n──────────────────────────────────────────────────────────────────────")
    print("[🧠] Temporal Risk View – Top Targets")
    print("──────────────────────────────────────────────────────────────────────")

    if not has_actionable:
        print("✓ No actionable temporal risk detected")
        print("\nReason:")
        print(" • No NEW subdomains with impact")
        print(" • No ESCALATED subdomains")
        print(" • All changes classified as LOW or DORMANT")
        print("──────────────────────────────────────────────────────────────────────")
    else:
        print_top_temporal(ranking)

    # ───────── Reactions ─────────
    output_dir = os.path.join(ctx.scan_dir, "reactions")
    os.makedirs(output_dir, exist_ok=True)

    for score, sub, state, action in ranking:
        if action != 'IGNORE':
            react({
                'subdomain': sub,
                'state': state,
                'score': score,
                'action': action
            }, output_dir)


# --------------------------------------------------------------------------------------------------
# Main Orchestrator
# --------------------------------------------------------------------------------------------------
def start(ctx: ScanContext) -> None:
    bscan_whois_look(ctx.target)

    if ctx.bruteforce:
        return run_bruteforce(ctx)

    if ctx.savemap:
        return run_map(ctx)

    run_enumeration(ctx)
    run_intelligence(ctx)


# --------------------------------------------------------------------------------------------------
def main() -> None:
    banner()
    args = parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    main_work_subdirs()

    ctx = ScanContext(
        target=args.domain,
        enum=args.enum,
        bruteforce=args.bruteforce,
        threads=args.threads,
        savemap=args.map,
        args=args
    )

    try:
        start(ctx)
    except KeyboardInterrupt:
        print(G + "\nTugaRecon interrupted by user" + W)
        sys.exit(130)


if __name__ == '__main__':
    main()
