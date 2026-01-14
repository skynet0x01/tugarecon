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
import subprocess
import os


# ----------------------------------------------------------------------------------------------------------
def react(entry, output_dir):
    """
    Executa reações automáticas com base na ação decidida
    """
    sub = entry["subdomain"]
    action = entry["action"]

    if action == "DEEP_HTTP_PROBE":
        run_httpx(sub, output_dir)

    elif action == "TLS_INSPECTION":
        run_tls(sub, output_dir)

    elif action == "HEADER_ANALYSIS":
        run_headers(sub, output_dir)

    elif action == "IGNORE":
        return


# ----------------------------------------------------------------------------------------------------------
def run_httpx(subdomain, output_dir):
    outfile = os.path.join(output_dir, "httpx_escalated.txt")

    cmd = [
        "httpx",
        "-u", f"https://{subdomain}",
        "-status-code",
        "-title",
        "-tech-detect",
        "-ip",
        "-silent"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=20
        )

        if result.stdout:
            with open(outfile, "a") as f:
                f.write(result.stdout)

    except Exception as e:
        pass


# ----------------------------------------------------------------------------------------------------------
def decide_action(subdomain, impact, temporal_state, temporal_score):
    if temporal_state == "ESCALATED":
        return "DEEP_HTTP_PROBE"

    if temporal_state == "NEW" and impact >= 20:
        return "HEADER_ANALYSIS"

    if temporal_state == "FLAPPING":
        return "WATCH"

    return "IGNORE"
