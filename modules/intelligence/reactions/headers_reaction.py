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

import requests
import json
import os
from datetime import datetime

TIMEOUT = 8

SECURITY_HEADERS = [
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy"
]

def run_headers(subdomain, output_dir):
    result = {
        "hostname": subdomain,
        "timestamp": datetime.utcnow().isoformat(),
        "headers": {},
        "missing": [],
        "weak_flags": []
    }

    url = f"https://{subdomain}"

    try:
        r = requests.get(url, timeout=TIMEOUT, verify=False)

        for h in SECURITY_HEADERS:
            if h in r.headers:
                result["headers"][h] = r.headers[h]
            else:
                result["missing"].append(h)

        if "Strict-Transport-Security" not in r.headers:
            result["weak_flags"].append("NO_HSTS")

        if "Content-Security-Policy" not in r.headers:
            result["weak_flags"].append("NO_CSP")

    except Exception as e:
        result["error"] = str(e)

    # persistência
    os.makedirs(output_dir, exist_ok=True)
    out_file = os.path.join(output_dir, "headers.json")

    with open(out_file, "w") as f:
        json.dump(result, f, indent=2)

    return result
