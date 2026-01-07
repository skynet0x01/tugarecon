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
from collections import Counter
import re


class PatternModel:
    def __init__(self):
        self.tokens = Counter()
        self.bigrams = Counter()

    def train(self, subdomains: list[str]):
        for sub in subdomains:
            parts = re.split(r"[.-]", sub)
            parts = [p for p in parts if p]

            for p in parts:
                self.tokens[p] += 1

            for i in range(len(parts) - 1):
                self.bigrams[(parts[i], parts[i + 1])] += 1

    def top_tokens(self, n: int = 10) -> list[str]:
        return [t for t, _ in self.tokens.most_common(n)]

    def top_bigrams(self, n: int = 10) -> list[tuple[str, str]]:
        return [b for b, _ in self.bigrams.most_common(n)]
