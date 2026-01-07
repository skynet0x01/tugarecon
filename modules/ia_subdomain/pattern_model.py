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
