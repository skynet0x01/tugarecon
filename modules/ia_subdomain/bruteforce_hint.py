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

COMMON_SERVICE_HINTS = {
    "admin": ["console", "panel", "dashboard", "manage"],
    "auth": ["sso", "login", "oauth", "keycloak"],
    "api": ["api-v1", "api-v2", "graphql", "internal-api"],
    "internal": ["vpn", "intranet", "corp", "lan"],
}

def generate_hints(semantic_results):
    hints = set()

    for r in semantic_results:
        tags = r.get("tags", [])
        for t in tags:
            for h in COMMON_SERVICE_HINTS.get(t, []):
                hints.add(h)

    return sorted(hints)
