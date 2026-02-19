# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Modules: modules/IA/pattern_model.py
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

from collections import Counter
import re


class PatternModel:
    """
    Lightweight statistical pattern extractor for subdomain names.

    This is NOT a predictive AI model.
    It is purely frequency-based and deterministic.

    It learns:
      - Token frequency
      - Bigram frequency
      - Trigram frequency

    It is used exclusively to assist candidate generation.
    """

    def __init__(self):
        # Individual token frequency
        self.tokens = Counter()

        # Adjacent token pairs (token1, token2)
        self.bigrams = Counter()

        # Adjacent token triples (token1, token2, token3)
        self.trigrams = Counter()

    # ----------------------------------------------------------------------------------------------
    # TRAINING
    # ----------------------------------------------------------------------------------------------

    def train(self, subdomains: list[str]):
        """
        Extract tokens and n-grams from a list of subdomains.

        Example:
            api-dev.internal.example.com
        Tokens extracted:
            api, dev, internal, example, com
        """

        for sub in subdomains:
            # Normalize
            sub = sub.lower()

            # Split by dot or dash
            parts = re.split(r"[.-]", sub)

            # Clean tokens:
            # - remove empty
            # - remove very short tokens (1 char)
            # - ignore pure numbers
            parts = [
                p for p in parts
                if p and len(p) > 1 and not p.isdigit()
            ]

            # Count individual tokens
            for p in parts:
                self.tokens[p] += 1

            # Count bigrams
            for i in range(len(parts) - 1):
                self.bigrams[(parts[i], parts[i + 1])] += 1

            # Count trigrams
            for i in range(len(parts) - 2):
                self.trigrams[(parts[i], parts[i + 1], parts[i + 2])] += 1

    # ----------------------------------------------------------------------------------------------
    # INSPECTION METHODS
    # ----------------------------------------------------------------------------------------------

    def top_tokens(self, n: int = 10) -> list[str]:
        """
        Return the top N most frequent tokens.
        """
        return [t for t, _ in self.tokens.most_common(n)]

    def top_bigrams(self, n: int = 10) -> list[tuple[str, str]]:
        """
        Return the top N most frequent bigrams.
        """
        return [b for b, _ in self.bigrams.most_common(n)]

    def top_trigrams(self, n: int = 10) -> list[tuple[str, str, str]]:
        """
        Return the top N most frequent trigrams.
        """
        return [t for t, _ in self.trigrams.most_common(n)]

    # ----------------------------------------------------------------------------------------------
    # SCORING
    # ----------------------------------------------------------------------------------------------

    def score_token(self, token: str) -> float:
        """
        Score a token based on its relative frequency.
        """
        total = sum(self.tokens.values()) or 1
        return self.tokens[token] / total

    def score_bigram(self, a: str, b: str) -> float:
        """
        Score a bigram based on relative frequency.
        """
        total = sum(self.bigrams.values()) or 1
        return self.bigrams[(a, b)] / total

    def score_trigram(self, a: str, b: str, c: str) -> float:
        """
        Score a trigram based on relative frequency.
        """
        total = sum(self.trigrams.values()) or 1
        return self.trigrams[(a, b, c)] / total

    # ----------------------------------------------------------------------------------------------
    # CANDIDATE GENERATION
    # ----------------------------------------------------------------------------------------------

    def generate_candidates(self, n_tokens: int = 10) -> set[str]:
        """
        Generate candidate subdomain fragments based on
        most frequent tokens and n-grams.

        This does NOT guess unseen words.
        It only recombines statistically common patterns.
        """

        candidates = set()

        top_tokens = self.top_tokens(n_tokens)
        top_bigrams = self.top_bigrams(n_tokens)
        top_trigrams = self.top_trigrams(n_tokens)

        # Single tokens
        for t in top_tokens:
            candidates.add(t)

        # Join bigrams
        for a, b in top_bigrams:
            candidates.add(f"{a}-{b}")
            candidates.add(f"{a}.{b}")

        # Join trigrams
        for a, b, c in top_trigrams:
            candidates.add(f"{a}-{b}-{c}")
            candidates.add(f"{a}.{b}.{c}")

        return candidates
