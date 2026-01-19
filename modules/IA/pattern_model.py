# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
from collections import Counter
import re


class PatternModel:
    """
    Lightweight statistical pattern extractor for subdomain names.
    This is NOT a predictive model, only a frequency-based learner.
    Used exclusively for candidate generation.
    """

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
