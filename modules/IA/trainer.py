# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Module: modules/IA/trainer.py
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
import os
from datetime import datetime
from modules.IA.ia_generator import IASubdomainGenerator
from modules.IA.ia_wordlist import enrich_wordlist_from_ia

def run_ia_training(target: str) -> None:
    base_dir = f"results/{target}"
    if not os.path.isdir(base_dir):
        return

    dates = []
    for d in os.listdir(base_dir):
        try:
            datetime.strptime(d, "%Y-%m-%d")
            dates.append(d)
        except ValueError:
            continue

    if not dates:
        return

    latest_date = sorted(dates)[-1]
    subdomains_file = os.path.join(
        base_dir, latest_date, "osint_subdomains.txt"
    )

    if not os.path.isfile(subdomains_file):
        return

    with open(subdomains_file) as f:
        found = [l.strip() for l in f if l.strip()]

    if len(found) < 2:
        print("[IA] Not enough data to generate patterns")
        return

    print(f"[IA] Training with {len(found)} subdomains")

    ia = IASubdomainGenerator(limit=1000)
    candidates = ia.generate(found)
    enrich_wordlist_from_ia(candidates)
