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
from modules.IA.heuristics import expand
from modules.IA.token_memory import get_token_weight


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
        # for token in self.model.top_tokens(10):
        #     token = token.strip().lower()
        #     if not token:
        #         continue
        #
        #     candidates.add(token)
        #
        #     for expanded in expand(token):
        #         candidates.add(expanded)

        # Tokens frequentes + memória inteligente
        ranked_tokens = []

        for token in self.model.top_tokens(30):  # buscamos mais, vamos filtrar depois
            token = token.strip().lower()
            if not token:
                continue

            weight = get_token_weight(token)
            ranked_tokens.append((token, weight))

        # ordenar por peso aprendido (descendente)
        ranked_tokens.sort(key=lambda x: x[1], reverse=True)

        # usar apenas os 10 melhores após ranking
        for token, _ in ranked_tokens[:10]:
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

        # NOTE: limit is applied globally to keep generation deterministic.
        # If needed, this can later be split per-source (tokens / bigrams).

        return final[:self.limit]
