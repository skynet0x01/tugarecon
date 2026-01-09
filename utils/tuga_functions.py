#!/usr/bin/python3
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
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

# import go here
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