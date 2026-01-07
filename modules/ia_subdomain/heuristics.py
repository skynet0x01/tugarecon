#!/usr/bin/python3
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01 2020-2025

# This file is part of TugaRecon, developed by skynet0x01 in 2020-2025.
#
# Copyright (C) 2025 skynet0x01
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

# Conhecimento operacional comum (heurísticas)
# Isto NÃO aprende: isto codifica hábitos reais de infra

ENVIRONMENTS = [
    "dev", "test", "testing",
    "qa", "uat",
    "stage", "staging",
    "preprod", "pre-prod",
    "prod", "production",
    "sandbox", "lab",
    "demo"
]

VERSIONS = [
    "v1", "v2", "v3",
    "v1beta", "v2beta",
    "v1alpha"
]

QUALIFIERS = [
    "internal",
    "private",
    "secure",
    "public",
    "backend",
    "frontend",
    "admin",
    "staff",
    "corp",
    "intranet",
    "vpn",
    "legacy",
    "old",
    "new"
]

API_LIKE_TOKENS = {
    "api", "apis", "rest", "graphql", "service", "services"
}


def expand(token: str) -> list[str]:
    """
    Gera expansões realistas para um token conhecido.
    Evita explosão combinatória desnecessária.
    """
    results = []

    # Ambientes
    for env in ENVIRONMENTS:
        results.append(f"{token}-{env}")

    # Versões apenas para tokens tipo API
    if token.lower() in API_LIKE_TOKENS:
        for v in VERSIONS:
            results.append(f"{token}-{v}")

    # Qualificadores
    for q in QUALIFIERS:
        results.append(f"{token}-{q}")

    return results
