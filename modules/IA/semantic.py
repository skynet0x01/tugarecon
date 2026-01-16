# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
import re

# =========================
# Administrative Interfaces
# =========================
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
    Perform semantic classification of a subdomain name.
    """

    subdomain = subdomain.strip().lower()
    tokens = re.split(r"[.-]", subdomain)

    tags = set()
    reasons = []

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

    env_matches = ENV_KEYWORDS & set(tokens)
    if env_matches:
        env = sorted(env_matches)[0]
        tags.add(env)
        reasons.append(f"{env} environment")

    risk = "LOW"
    if "admin" in tags and ("prod" in tags or "production" in tags):
        risk = "HIGH"
    elif "admin" in tags or "auth" in tags or "internal" in tags:
        risk = "MEDIUM"

    return {
        "subdomain": subdomain,
        "tags": sorted(tags),
        "risk_hint": risk,
        "reason": ", ".join(reasons) if reasons else "generic service"
    }
