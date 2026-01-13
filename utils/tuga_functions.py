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
import datetime
from utils.tuga_colors import G, Y, R, W

# ----------------------------------------------------------------------------------------------------------
def print_semantic_results(classified):
    """
    Wide, clean, professional semantic + impact output.
    Handles long real-world subdomains gracefully.
    """

    PRIORITY_COLOR = {
        "CRITICAL": R,
        "HIGH": R,
        "MEDIUM": Y,
        "LOW": G
    }

    classified = sorted(
        classified,
        key=lambda x: x.get("impact_score", 0),
        reverse=True
    )

    print("\n[🧠] Semantic & Impact Classification\n")
    print(" #   PRIORITY   IMPACT   SUBDOMAIN                                                     TAGS")
    print("-" * 95)

    for idx, item in enumerate(classified, 1):
        priority = item.get("priority", "LOW")
        impact = item.get("impact_score", 0)
        pcolor = PRIORITY_COLOR.get(priority, W)

        subdomain = item.get("subdomain", "").strip()
        tags = ", ".join(item.get("tags", [])) if item.get("tags") else "-"

        print(
            f"{idx:>3}   "
            f"{pcolor}{priority:<9}{W} "
            f"{impact:>6}   "
            f"{subdomain:<60} "
            f"{tags}"
        )

    print()

# ----------------------------------------------------------------------------------------------------------
def print_semantic_results_grouped(results):
    high_medium = []
    low = []

    for r in results:
        priority = r.get("priority", "LOW")
        impact = r.get("impact", 0)

        r["_priority"] = priority
        r["_impact"] = impact

        if priority in ("HIGH", "MEDIUM"):
            high_medium.append(r)
        else:
            low.append(r)

    print("\n" + "─" * 60)
    print("[🧠] Semantic & Impact Classification")
    print("─" * 60)

    if high_medium:
        print("\n[ HIGH | MEDIUM PRIORITY ]")
        print("-" * 80)
        print(" #   PRIORITY   IMPACT   SUBDOMAIN")
        print("-" * 80)

        for i, r in enumerate(high_medium, 1):
            tags = ", ".join(r.get("tags", [])) or "-"
            sub = r.get("subdomain", "unknown")

            print(
                f"{i:3}   {r['_priority']:<7}   {r['_impact']:>6}   "
                f"{sub:<45} [{tags}]"
            )

    if low:
        print("\n" + "─" * 60)
        print("[ LOW PRIORITY ]")
        print("-" * 80)

        offset = len(high_medium)
        for i, r in enumerate(low, offset + 1):
            sub = r.get("subdomain", "unknown")

            print(
                f"{i:3}   {r['_priority']:<7}   {r['_impact']:>6}   "
                f"{sub}"
            )
