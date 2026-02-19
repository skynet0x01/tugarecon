# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Module: modules/IA/ia_generator.py
#
# IASubdomainGenerator is responsible for generating new subdomain candidates
# based on learned patterns and controlled heuristics.
# It does not perform validation, scanning, or scoring.
#
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
from modules.IA.pattern_model import PatternModel
from modules.IA.heuristics import expand_weighted
from modules.IA.token_memory import get_token_weight


class IASubdomainGenerator:
    def __init__(self, limit: int = 500):
        self.model = PatternModel()
        self.limit = limit

    def generate(self, known_subdomains: list[str]) -> list[str]:
        self.model.train(known_subdomains)

        candidate_scores = {}

        # -----------------------------
        # 1️⃣ Tokens frequentes + peso aprendido
        # -----------------------------
        ranked_tokens = []

        for token in self.model.top_tokens(30):
            token = token.strip().lower()
            if not token:
                continue

            base_weight = get_token_weight(token)
            ranked_tokens.append((token, base_weight))

        # ordenar por peso aprendido (descendente)
        ranked_tokens.sort(key=lambda x: x[1], reverse=True)

        # usar apenas os 10 melhores após ranking
        for token, base_weight in ranked_tokens[:10]:
            candidate_scores[token] = base_weight

            # expansões com peso
            for expanded, expansion_weight in expand_weighted(token):
                combined = base_weight * expansion_weight
                candidate_scores[expanded] = combined

        # -----------------------------
        # 2️⃣ Bigramas com score próprio
        # -----------------------------
        for a, b in self.model.top_bigrams(10):
            a, b = a.lower(), b.lower()

            # peso baseado na soma dos tokens
            weight_a = get_token_weight(a)
            weight_b = get_token_weight(b)

            combined_score = (weight_a + weight_b) / 2

            candidate_scores[f"{a}-{b}"] = combined_score
            candidate_scores[f"{b}-{a}"] = combined_score * 0.95  # ligeira penalização reverso

        # -----------------------------
        # 3️⃣ Ordenar por score descendente
        # -----------------------------
        final = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)

        return [name for name, _ in final[:self.limit]]

