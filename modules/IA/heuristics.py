# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

# Conhecimento operacional comum (heurísticas)
# Isto NÃO aprende: isto codifica hábitos reais de infra

# ------------------------------------------------------------
# Heuristic token expansion for adaptive subdomain generation
# ------------------------------------------------------------

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
    "api", "apis", "rest", "graphql",
    "service", "services"
}

# Tokens fortemente associados a software de gestão
MANAGEMENT_TOKENS = {
    # Generic management
    "admin", "portal", "dashboard", "console", "panel", "manager",

    # ERP / CRM / ITSM
    "erp", "crm", "sap", "s4", "hana", "odoo",
    "servicenow", "snow", "jira", "confluence",

    # Identity / access
    "auth", "login", "sso", "iam", "id", "identity",
    "keycloak", "okta",

    # Infrastructure / monitoring
    "grafana", "prometheus", "kibana", "elastic",
    "zabbix", "nagios",

    # CI/CD & code management
    "git", "gitlab", "jenkins", "ci", "cd",
    "registry", "nexus", "harbor",

    # Network / internal IT
    "vpn", "proxy", "firewall", "fw", "mdm"
}


def expand(token: str) -> list[str]:
    """
    Gera expansões realistas e inteligentes para um token conhecido.
    - Evita explosão combinatória
    - Aplica versões apenas onde faz sentido
    - Usa heurísticas baseadas em software de gestão real
    """
    token = token.lower()
    results: set[str] = set()

    # 1. Ambientes (sempre seguros)
    for env in ENVIRONMENTS:
        results.add(f"{token}-{env}")

    # 2. Versões apenas para APIs e serviços versionáveis
    if token in API_LIKE_TOKENS:
        for v in VERSIONS:
            results.add(f"{token}-{v}")
            for env in ENVIRONMENTS:
                results.add(f"{token}-{v}-{env}")

    # 3. Qualificadores (limitados)
    for q in QUALIFIERS:
        results.add(f"{token}-{q}")

    # 4. Heurística especial para software de gestão
    if token in MANAGEMENT_TOKENS:
        for env in ("dev", "qa", "uat", "prod"):
            results.add(f"{token}-{env}")
        for q in ("internal", "admin", "corp"):
            results.add(f"{token}-{q}")

    return sorted(results)
