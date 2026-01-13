#!/usr/bin/python3
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save into a file
# Coded By skynet0x01 2020-2026

# This file is part of TugaRecon, developed by skynet0x01 in 2020-2025.
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
import json
import os
from datetime import datetime

def load_scan(target, date):
    path = f"results/{target}/{date}/semantic_results.json"
    if not os.path.exists(path):
        return []

    with open(path) as f:
        return json.load(f)


def diff_scans(target: str, old_date: str, new_date: str) -> dict:
    """
    Compare two scans by date for a given target.
    Returns a dict with keys:
      - new: subdomains found only in the latest scan
      - removed: subdomains present only in the previous scan
      - updated: subdomains with changed impact scores or tags
    """
    old_path = os.path.join("results", target, old_date, "semantic_results.json")
    new_path = os.path.join("results", target, new_date, "semantic_results.json")

    if not os.path.exists(old_path):
        print(f"[!] Previous scan file not found: {old_path}")
        return {}

    if not os.path.exists(new_path):
        print(f"[!] Current scan file not found: {new_path}")
        return {}

    with open(old_path, "r") as f:
        old_results = {r["subdomain"]: r for r in json.load(f)}

    with open(new_path, "r") as f:
        new_results = {r["subdomain"]: r for r in json.load(f)}

    diff = {"new": [], "removed": [], "updated": []}

    # Detect new and updated subdomains
    for sub, r in new_results.items():
        if sub not in old_results:
            diff["new"].append(r)
        else:
            old_r = old_results[sub]
            if r.get("impact_score") != old_r.get("impact_score") or set(r.get("tags", [])) != set(old_r.get("tags", [])):
                diff["updated"].append({
                    "subdomain": sub,
                    "old_score": old_r.get("impact_score", 0),
                    "new_score": r.get("impact_score", 0),
                    "tags": r.get("tags", []),
                })

    # Detect removed subdomains
    for sub, r in old_results.items():
        if sub not in new_results:
            diff["removed"].append(r)

    return diff



def export_diff(diff, target, date):
    base = f"results/{target}/{date}"
    os.makedirs(base, exist_ok=True)

    path = os.path.join(base, "scan_diff.json")

    with open(path, "w") as f:
        json.dump(diff, f, indent=2)

    return path


def get_previous_scan_date(target, today):
    base = f"results/{target}"
    if not os.path.exists(base):
        return None

    dates = sorted(
        d for d in os.listdir(base)
        if d < today and os.path.isdir(os.path.join(base, d))
    )

    return dates[-1] if dates else None
