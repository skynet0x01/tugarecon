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

# -------------------------------------------------------------------
# Domain knowledge: environments, versions and qualifiers
# -------------------------------------------------------------------
"""
Heuristic token expansion engine
Extended with SCADA / ICS and vertical-specific intelligence.

This module is intentionally conservative:
- No combinatorial explosions
- Deterministic output
- Sector-aware heuristics (Energy, Water, Manufacturing)
- Designed for enterprise and academic reconnaissance
"""

# -------------------------------------------------------------------
# Generic domain knowledge
# -------------------------------------------------------------------

ENVIRONMENTS = [
    "dev", "test", "testing",
    "qa", "uat",
    "stage", "staging",
    "preprod", "pre-prod",
    "prod", "production",
    "lab", "sandbox",
]

VERSIONS = [
    "v1", "v2", "v3",
    "v1alpha", "v1beta",
]

QUALIFIERS = [
    "internal", "private", "secure",
    "public", "backend", "frontend",
    "admin", "staff", "corp",
    "intranet", "vpn",
    "legacy", "old", "new",
]

# -------------------------------------------------------------------
# Semantic categories (IT)
# -------------------------------------------------------------------

API_LIKE_TOKENS = {
    "api", "apis", "rest", "graphql",
    "service", "services",
}

MANAGEMENT_TOKENS = {
    "admin", "portal", "dashboard", "console", "panel",
    "erp", "crm", "sap", "s4", "hana", "odoo",
    "servicenow", "snow", "jira", "confluence",
    "auth", "login", "sso", "iam", "identity",
    "keycloak", "okta",
    "grafana", "prometheus", "kibana", "elastic",
    "zabbix", "nagios",
    "git", "gitlab", "jenkins", "ci", "cd",
    "vpn", "proxy", "firewall", "fw",
}

# -------------------------------------------------------------------
# SCADA / ICS – Core domains
# -------------------------------------------------------------------

SCADA_CONTROL_TOKENS = {
    "plc", "rtu", "ied", "hmi", "pac", "dcu", "mtu",
    "controller", "logic", "gateway",
    "field", "node", "station",
    "modbus", "dnp3", "bacnet", "opc", "profinet",
}

SCADA_MONITOR_TOKENS = {
    "scada", "supervisory", "monitor", "view",
    "operator", "cockpit", "dashboard",
    "historian", "history", "log", "archive",
    "sql-scada", "db-ics",
    "ems", "dms", "bms",
}

SCADA_REMOTE_TOKENS = {
    "remote-scada", "vpn-ot",
    "eng", "engineering",
    "config", "setup", "admin-scada",
    "maintenance", "service",
    "support-ics", "portal-ot",
}

# -------------------------------------------------------------------
# SCADA – Vertical-specific domains
# -------------------------------------------------------------------

SCADA_ENERGY_TOKENS = {
    "grid", "substation", "solar", "wind",
    "meter", "smartgrid", "transformer",
}

SCADA_WATER_TOKENS = {
    "pump", "well", "treatment",
    "flow", "tank", "valve", "reservoir",
}

SCADA_MANUFACTURING_TOKENS = {
    "plant", "factory", "line1",
    "cell", "mes",
}

SCADA_TOKENS = (
    SCADA_CONTROL_TOKENS
    | SCADA_MONITOR_TOKENS
    | SCADA_REMOTE_TOKENS
    | SCADA_ENERGY_TOKENS
    | SCADA_WATER_TOKENS
    | SCADA_MANUFACTURING_TOKENS
)

# -------------------------------------------------------------------
# Expansion engine
# -------------------------------------------------------------------

def expand(token: str) -> list[str]:
    """
    Generate realistic subdomain expansions for a token.

    Rules:
    - Environments always apply
    - Versions only for API-like tokens
    - Management systems get admin/internal bias
    - SCADA tokens follow OT-safe patterns
    - Vertical-specific rules enhance realism
    """
    token = token.lower()
    expansions: set[str] = set()

    # 1. Base environment expansion
    for env in ENVIRONMENTS:
        expansions.add(f"{token}-{env}")

    # 2. API-like versioning
    if token in API_LIKE_TOKENS:
        for version in VERSIONS:
            expansions.add(f"{token}-{version}")
            for env in ENVIRONMENTS:
                expansions.add(f"{token}-{version}-{env}")

    # 3. Generic qualifiers
    for qualifier in QUALIFIERS:
        expansions.add(f"{token}-{qualifier}")

    # 4. Management systems heuristic
    if token in MANAGEMENT_TOKENS:
        for env in ("dev", "qa", "uat", "prod"):
            expansions.add(f"{token}-{env}")
        for qualifier in ("admin", "internal", "corp"):
            expansions.add(f"{token}-{qualifier}")

    # 5. Generic SCADA / OT heuristic
    if token in SCADA_TOKENS:
        for env in ("prod", "uat", "qa"):
            expansions.add(f"{token}-{env}")
        for qualifier in ("control", "operator", "internal"):
            expansions.add(f"{token}-{qualifier}")

    # 6. Energy sector heuristic
    if token in SCADA_ENERGY_TOKENS:
        for suffix in ("grid", "substation", "control"):
            expansions.add(f"{token}-{suffix}")

    # 7. Water sector heuristic
    if token in SCADA_WATER_TOKENS:
        for suffix in ("plant", "control", "monitor"):
            expansions.add(f"{token}-{suffix}")

    # 8. Manufacturing heuristic
    if token in SCADA_MANUFACTURING_TOKENS:
        for suffix in ("line", "cell", "control", "mes"):
            expansions.add(f"{token}-{suffix}")

    return sorted(expansions)

