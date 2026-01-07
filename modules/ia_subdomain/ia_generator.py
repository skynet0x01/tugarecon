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

# import go here
# ----------------------------------------------------------------------------------------------------------
from .pattern_model import PatternModel
from .heuristics import expand


class IASubdomainGenerator:
    def __init__(self, limit: int = 500):
        self.model = PatternModel()
        self.limit = limit

    def generate(self, known_subdomains: list[str]) -> list[str]:
        """
        Recebe subdomínios SEM o domínio (ex: 'api-prod')
        Retorna apenas nomes de subdomínio (sem '.example.com')
        """
        self.model.train(known_subdomains)

        candidates = set()

        # Tokens frequentes
        for token in self.model.top_tokens(10):
            token = token.strip().lower()
            if not token:
                continue

            candidates.add(token)

            for expanded in expand(token):
                candidates.add(expanded)

        # Bigramas (ordem importa)
        for a, b in self.model.top_bigrams(10):
            a, b = a.lower(), b.lower()
            candidates.add(f"{a}-{b}")
            candidates.add(f"{b}-{a}")

        # Limitar e ordenar (determinístico)
        final = sorted(candidates)
        return final[:self.limit]
