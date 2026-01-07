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
