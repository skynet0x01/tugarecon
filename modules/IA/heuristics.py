# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Model: models/IA/heuristics.py
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

"""
Heuristic token expansion engine
Extended with multi-sector intelligence.

This module is intentionally conservative:
- No combinatorial explosions
- Deterministic output
- Sector-aware heuristics (IT, Finance, Health, Telco, Gov, Edu, OT)
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
# Semantic categories (IT / Enterprise)
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
# FINANCE / BANKING
# -------------------------------------------------------------------

FINANCE_TOKENS = {
    "corebank", "banking", "core-banking",
    "swift", "sepa", "ach",
    "atm", "pos", "terminal",
    "payments", "pay", "billing", "invoice",
    "card", "cards", "visa", "mastercard",
    "fraud", "aml", "kyc",
    "treasury", "trading", "broker",
    "risk", "compliance",
    "ledger", "accounting", "accounts",
}

# -------------------------------------------------------------------
# HEALTH
# -------------------------------------------------------------------

HEALTH_TOKENS = {
    "his", "ris", "pacs",
    "ehr", "emr",
    "hl7", "fhir", "dicom",
    "radiology", "lab", "lis",
    "pharmacy", "prescription",
    "patient", "clinical",
    "imaging", "scan",
    "billing-health",
}

# -------------------------------------------------------------------
# TELCO
# -------------------------------------------------------------------

TELCO_TOKENS = {
    "core-net", "bss", "oss",
    "hlr", "hss", "ims",
    "msc", "sgw", "pgw",
    "cdr", "billing-telco",
    "provisioning", "radius",
    "voip", "sip",
    "lte", "5g", "nr",
}

# -------------------------------------------------------------------
# GOVERNMENT
# -------------------------------------------------------------------

GOV_TOKENS = {
    "citizen", "portal-cidadao",
    "tax", "financas",
    "justice", "court",
    "police", "psp", "gnr",
    "customs", "immigration",
    "eproc", "procurement",
    "registry", "civil",
    "election", "voting",
}

# -------------------------------------------------------------------
# EDUCATION
# -------------------------------------------------------------------

EDU_TOKENS = {
    "campus", "student", "students",
    "teacher", "staff",
    "moodle", "lms",
    "exam", "grades",
    "library", "repo",
    "admissions", "enroll",
    "alumni",
}

# -------------------------------------------------------------------
# E-COMMERCE / RETAIL
# -------------------------------------------------------------------

ECOMMERCE_TOKENS = {
    "shop", "store",
    "cart", "checkout",
    "orders", "order",
    "catalog", "inventory",
    "warehouse", "fulfillment",
    "payment", "gateway",
    "customer", "crm-retail",
    "returns", "refund",
}

# -------------------------------------------------------------------
# Expansion engine
# -------------------------------------------------------------------
def expand_weighted(token: str) -> list[tuple[str, float]]:
    """
    Expande um token e associa um peso heurístico (0.0 – 1.0).

    Filosofia:
    - Peso alto → altamente provável em ambientes reais
    - Peso médio → comum mas dependente de maturidade da organização
    - Peso baixo → plausível mas menos frequente
    - Determinístico
    """

    token = token.lower()
    expansions: dict[str, float] = {}

    def add(candidate: str, weight: float):
        # Mantém sempre o maior peso caso exista duplicação
        if candidate not in expansions or expansions[candidate] < weight:
            expansions[candidate] = weight

    # ------------------------------------------------------------------
    # 1. Ambientes universais
    # ------------------------------------------------------------------

    for env in ENVIRONMENTS:
        if env in ("prod", "production"):
            add(f"{token}-{env}", 0.95)
        elif env in ("dev", "test", "qa", "uat"):
            add(f"{token}-{env}", 0.85)
        else:
            add(f"{token}-{env}", 0.70)

    # ------------------------------------------------------------------
    # 2. Qualificadores globais
    # ------------------------------------------------------------------

    for qualifier in QUALIFIERS:
        if qualifier in ("internal", "admin", "secure"):
            add(f"{token}-{qualifier}", 0.80)
        else:
            add(f"{token}-{qualifier}", 0.65)

    # ------------------------------------------------------------------
    # 3. API / Versionamento
    # ------------------------------------------------------------------

    if token in API_LIKE_TOKENS:
        for version in VERSIONS:
            add(f"{token}-{version}", 0.88)

            for env in ENVIRONMENTS:
                if env in ("prod", "production"):
                    add(f"{token}-{version}-{env}", 0.82)
                else:
                    add(f"{token}-{version}-{env}", 0.72)

    # ------------------------------------------------------------------
    # 4. Management / Admin Systems
    # ------------------------------------------------------------------

    if token in MANAGEMENT_TOKENS:
        for env in ("dev", "qa", "uat", "prod"):
            add(f"{token}-{env}", 0.92)

        for q in ("admin", "internal", "corp", "secure"):
            add(f"{token}-{q}", 0.90)

    # ------------------------------------------------------------------
    # 5. SCADA / OT (aqui o risco real começa)
    # ------------------------------------------------------------------

    if token in SCADA_TOKENS:
        for env in ("prod", "uat", "qa"):
            add(f"{token}-{env}", 0.93)

        for q in ("control", "operator", "internal", "eng"):
            add(f"{token}-{q}", 0.91)

    if token in SCADA_ENERGY_TOKENS:
        for suffix in ("grid", "substation", "control", "dispatch"):
            add(f"{token}-{suffix}", 0.89)

    if token in SCADA_WATER_TOKENS:
        for suffix in ("plant", "control", "monitor", "treatment"):
            add(f"{token}-{suffix}", 0.88)

    if token in SCADA_MANUFACTURING_TOKENS:
        for suffix in ("line", "cell", "control", "mes", "robot"):
            add(f"{token}-{suffix}", 0.87)

    # ------------------------------------------------------------------
    # 6. Finance (muito padronizado)
    # ------------------------------------------------------------------

    if token in FINANCE_TOKENS:
        for env in ("prod", "uat", "qa", "dr"):
            add(f"{token}-{env}", 0.94)

        for q in ("secure", "internal", "core", "settlement"):
            add(f"{token}-{q}", 0.91)

    # ------------------------------------------------------------------
    # 7. Health
    # ------------------------------------------------------------------

    if token in HEALTH_TOKENS:
        for env in ("prod", "test", "dr"):
            add(f"{token}-{env}", 0.93)

        for q in ("internal", "secure", "clinical", "patient"):
            add(f"{token}-{q}", 0.90)

    # ------------------------------------------------------------------
    # 8. Telco
    # ------------------------------------------------------------------

    if token in TELCO_TOKENS:
        for env in ("prod", "lab", "test"):
            add(f"{token}-{env}", 0.92)

        for q in ("internal", "net", "core", "edge"):
            add(f"{token}-{q}", 0.89)

    # ------------------------------------------------------------------
    # 9. Government
    # ------------------------------------------------------------------

    if token in GOV_TOKENS:
        for env in ("prod", "uat", "dr"):
            add(f"{token}-{env}", 0.94)

        for q in ("public", "internal", "secure", "gov"):
            add(f"{token}-{q}", 0.91)

    # ------------------------------------------------------------------
    # 10. Education
    # ------------------------------------------------------------------

    if token in EDU_TOKENS:
        for env in ("prod", "test"):
            add(f"{token}-{env}", 0.85)

        for q in ("internal", "academic", "campus"):
            add(f"{token}-{q}", 0.83)

    # ------------------------------------------------------------------
    # 11. E-commerce
    # ------------------------------------------------------------------

    if token in ECOMMERCE_TOKENS:
        for env in ("prod", "staging", "test"):
            add(f"{token}-{env}", 0.90)

        for q in ("secure", "internal", "backend", "payments"):
            add(f"{token}-{q}", 0.88)

    # ------------------------------------------------------------------
    # Output determinístico ordenado por peso descendente
    # ------------------------------------------------------------------

    return sorted(expansions.items(), key=lambda x: x[1], reverse=True)
