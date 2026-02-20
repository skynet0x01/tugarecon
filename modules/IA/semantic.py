# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Model: modules/IA/semantics.py
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
import re

"""
Este módulo faz classificação semântica de subdomínios.

Objetivo:
    A partir do nome de um subdomínio (ex: admin.prod.example.com),
    inferir:
        - tipo de serviço
        - contexto (admin, api, auth, etc.)
        - ambiente (dev, prod, staging...)
        - hint de risco baseado na combinação de tags

Importante:
    Isto NÃO é detecção de vulnerabilidades.
    É apenas enriquecimento semântico baseado em naming conventions.
"""


# =========================
# Administrative Interfaces
# =========================
# Termos normalmente associados a painéis administrativos
# ou interfaces privilegiadas.
ADMIN_KEYWORDS = {
    "admin", "administrator", "admins",
    "manage", "management", "manager",
    "console", "dashboard",
    "panel", "control", "controlpanel",
    "cpanel", "plesk",
    "webadmin", "sysadmin",
    "ops", "operator", "operators",
    "superuser", "root",
    "maint", "maintenance"
}


# =========================
# Internal / Corporate Access
# =========================
# Termos que sugerem acesso interno, corporativo ou restrito.
INTERNAL_KEYWORDS = {
    "internal", "intranet",
    "corp", "corporate",
    "lan", "wan",
    "private", "priv",
    "vpn", "tunnel",
    "office", "hq",
    "backend", "backoffice",
    "int", "inside",
    "restricted", "securezone"
}


# =========================
# API / Service Endpoints
# =========================
# Naming comum em microservices e integrações.
API_KEYWORDS = {
    "api", "apis",
    "rest", "restful",
    "graphql", "gql",
    "rpc", "grpc",
    "service", "services",
    "svc", "microservice", "ms",
    "endpoint", "endpoints",
    "integration", "integrations",
    "webhook", "hooks"
}


# =========================
# Authentication / Identity
# =========================
# Termos relacionados com identidade e controlo de acesso.
AUTH_KEYWORDS = {
    "auth", "authentication",
    "login", "logout",
    "signin", "signon",
    "sso", "saml",
    "oauth", "oauth2", "oidc",
    "keycloak",
    "iam", "id", "identity",
    "accounts", "account",
    "users", "user",
    "access", "accesscontrol",
    "credentials", "cred"
}


# =========================
# Environments / Lifecycle
# =========================
# Termos que indicam ambiente de execução.
# Isto é extremamente útil para priorização de risco.
ENV_KEYWORDS = {
    # Development & testing
    "dev", "develop", "development",
    "test", "testing",
    "qa", "quality",
    "uat",

    # Pre-production
    "stage", "staging",
    "preprod", "pre-prod",
    "preview", "beta", "alpha",
    "sandbox", "lab", "demo",

    # Production
    "prod", "production", "live",
    "release"
}


def classify(subdomain: str) -> dict:
    """
    Classifica semanticamente um subdomínio.

    Processo:
        1. Normaliza o nome
        2. Divide em tokens por '.' e '-'
        3. Procura interseção com conjuntos de palavras-chave
        4. Enriquece com análise por substring (infra/cloud/etc)
        5. Gera hint de risco baseado na combinação de tags

    Retorna:
        dict com:
            - subdomain
            - tags (lista ordenada)
            - risk_hint (LOW/MEDIUM/HIGH)
            - reason (explicação textual)
    """

    # Normalização básica
    subdomain = subdomain.strip().lower()

    # Divide por ponto ou hífen.
    # Exemplo:
    #   admin-prod.api.example.com
    # -> ["admin", "prod", "api", "example", "com"]
    tokens = re.split(r"[.-]", subdomain)

    # Versão completa para análises por substring
    # (quando a keyword não aparece isolada como token)
    full = subdomain

    tags = set()
    reasons = []

    # -------------------------
    # Classificação por tokens exatos
    # -------------------------

    # Se houver interseção entre tokens e palavras admin
    if ADMIN_KEYWORDS & set(tokens):
        tags.add("admin")
        reasons.append("administrative interface")

    if INTERNAL_KEYWORDS & set(tokens):
        tags.add("internal")
        reasons.append("internal-only naming")

    if API_KEYWORDS & set(tokens):
        tags.add("api")
        reasons.append("API/service endpoint")

    if AUTH_KEYWORDS & set(tokens):
        tags.add("auth")
        reasons.append("authentication-related service")

    # Ambiente (dev, prod, staging, etc.)
    env_matches = ENV_KEYWORDS & set(tokens)
    if env_matches:
        # Se houver mais que um, escolhe o primeiro alfabeticamente
        # (decisão simples, pode ser refinada no futuro)
        env = sorted(env_matches)[0]
        tags.add(env)
        reasons.append(f"{env} environment")

    # -------------------------
    # Enriquecimento por substring
    # -------------------------
    # Aqui não exigimos token exato.
    # Basta a palavra existir dentro do subdomínio.

    if any(k in full for k in ["gateway", "proxy", "ingress"]):
        tags.add("gateway")
        reasons.append("network gateway")

    if any(k in full for k in ["akamai", "cdn", "fastly", "cloudfront"]):
        tags.add("cdn")
        tags.add("edge")
        reasons.append("edge/CDN infrastructure")

    if any(k in full for k in ["delivery", "route", "lb", "balancer"]):
        tags.add("loadbalancer")
        tags.add("infra")
        reasons.append("traffic delivery infrastructure")

    if any(k in full for k in ["cloud", "aws", "azure", "gcp"]):
        tags.add("cloud")
        reasons.append("cloud infrastructure")

    if any(k in full for k in ["monitor", "grafana", "kibana", "sentry", "prometheus"]):
        tags.add("monitoring")
        reasons.append("monitoring system")

    if any(k in full for k in ["voice", "sip", "voip", "telecom"]):
        tags.add("telecom")
        reasons.append("telecommunications service")

    # -------------------------
    # Heurística de risco
    # -------------------------
    # Isto é apenas um hint baseado em combinação de tags.
    # Não é uma métrica de vulnerabilidade real.

    risk = "LOW"

    # Admin exposto em produção → prioridade alta
    if "admin" in tags and ("prod" in tags or "production" in tags):
        risk = "HIGH"

    # Serviços sensíveis mas sem confirmação de prod
    elif {"admin", "auth", "internal", "gateway", "cloud"} & tags:
        risk = "MEDIUM"

    # Estrutura final retornada
    return {
        "subdomain": subdomain,
        "tags": sorted(tags),
        "risk_hint": risk,
        "reason": ", ".join(reasons) if reasons else "generic service"
    }