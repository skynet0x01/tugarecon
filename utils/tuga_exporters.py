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
import datetime

def export_json(results: list, target: str, date: str,
                filename="semantic_results.json"):
    base = f"results/{target}/{date}"
    os.makedirs(base, exist_ok=True)

    path = os.path.join(base, filename)

    with open(path, "w") as f:
        json.dump(results, f, indent=2)

    return path


def export_priority_lists(results: list, target: str):
    date = str(datetime.datetime.now().date())
    base = f"results/{target}/{date}"
    os.makedirs(base, exist_ok=True)

    buckets = {
        "CRITICAL": [],
        "HIGH": []
    }

    for r in results:
        p = r.get("priority")
        if p in buckets:
            buckets[p].append(r)

    for level, items in buckets.items():
        if not items:
            continue

        path = os.path.join(base, f"{level.lower()}_targets.txt")
        with open(path, "w") as f:
            for r in items:
                f.write(
                    f"{r['subdomain']:<65} "
                    f"impact={r['impact_score']:>3} "
                    f"tags={','.join(r['tags'])}\n"
                )
