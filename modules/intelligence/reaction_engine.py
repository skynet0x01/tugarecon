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
import json

from modules.intelligence.reactions.tls_reaction import run_tls_reaction
from modules.intelligence.reactions.headers_reaction import run_headers
from modules.intelligence.reactions.httpx_reaction import run_httpx


REACTION_MAP = {
    "HTTPX": [run_httpx, run_tls_reaction, run_headers],
    "HTTP": [run_httpx],
    "DEEP_HTTP_PROBE": [run_httpx, run_tls_reaction, run_headers],
    "HEADER_ANALYSIS": [run_headers],
    "TLS_ONLY": [run_tls_reaction],
}

def react(entry, output_dir):
    sub = entry["subdomain"]
    action = entry["action"]

    sub_dir = os.path.join(output_dir, sub.replace("/", "_"))
    os.makedirs(sub_dir, exist_ok=True)

    metadata = {
        "subdomain": sub,
        "state": entry["state"],
        "impact": entry["impact"],
        "score": entry["score"],
        "action": action,
    }

    with open(os.path.join(sub_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    for reaction in REACTION_MAP.get(action, []):
        try:
            reaction(sub, sub_dir)
        except Exception as e:
            with open(os.path.join(sub_dir, "error.log"), "a") as f:
                f.write(str(e) + "\n")



# ----------------------------------------------------------------------------------------------------------
def decide_action(subdomain, impact, temporal_state, temporal_score):
    if temporal_state == "ESCALATED":
        return "HTTPX"

    if temporal_state == "NEW" and impact >= 20:
        return "HTTP"

    if temporal_state == "FLAPPING":
        return "WATCH"

    return "IGNORE"
