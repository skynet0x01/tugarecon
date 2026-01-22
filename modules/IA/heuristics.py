# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
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

def expand(token: str) -> list[str]:
    token = token.lower()
    expansions: set[str] = set()

    # Base environments
    for env in ENVIRONMENTS:
        expansions.add(f"{token}-{env}")

    # API-like versioning
    if token in API_LIKE_TOKENS:
        for version in VERSIONS:
            expansions.add(f"{token}-{version}")
            for env in ENVIRONMENTS:
                expansions.add(f"{token}-{version}-{env}")

    # Generic qualifiers
    for qualifier in QUALIFIERS:
        expansions.add(f"{token}-{qualifier}")

    # Management heuristic
    if token in MANAGEMENT_TOKENS:
        for env in ("dev", "qa", "uat", "prod"):
            expansions.add(f"{token}-{env}")
        for qualifier in ("admin", "internal", "corp"):
            expansions.add(f"{token}-{qualifier}")

    # SCADA / OT heuristic
    if token in SCADA_TOKENS:
        for env in ("prod", "uat", "qa"):
            expansions.add(f"{token}-{env}")
        for qualifier in ("control", "operator", "internal"):
            expansions.add(f"{token}-{qualifier}")

    if token in SCADA_ENERGY_TOKENS:
        for suffix in ("grid", "substation", "control"):
            expansions.add(f"{token}-{suffix}")

    if token in SCADA_WATER_TOKENS:
        for suffix in ("plant", "control", "monitor"):
            expansions.add(f"{token}-{suffix}")

    if token in SCADA_MANUFACTURING_TOKENS:
        for suffix in ("line", "cell", "control", "mes"):
            expansions.add(f"{token}-{suffix}")

    # Finance
    if token in FINANCE_TOKENS:
        for env in ("prod", "uat", "qa", "dr"):
            expansions.add(f"{token}-{env}")
        for q in ("secure", "internal", "core"):
            expansions.add(f"{token}-{q}")

    # Health
    if token in HEALTH_TOKENS:
        for env in ("prod", "test", "dr"):
            expansions.add(f"{token}-{env}")
        for q in ("internal", "secure", "clinical"):
            expansions.add(f"{token}-{q}")

    # Telco
    if token in TELCO_TOKENS:
        for env in ("prod", "lab", "test"):
            expansions.add(f"{token}-{env}")
        for q in ("internal", "net", "core"):
            expansions.add(f"{token}-{q}")

    # Government
    if token in GOV_TOKENS:
        for env in ("prod", "uat", "dr"):
            expansions.add(f"{token}-{env}")
        for q in ("public", "internal", "secure"):
            expansions.add(f"{token}-{q}")

    # Education
    if token in EDU_TOKENS:
        for env in ("prod", "test"):
            expansions.add(f"{token}-{env}")
        for q in ("internal", "academic"):
            expansions.add(f"{token}-{q}")

    # E-commerce
    if token in ECOMMERCE_TOKENS:
        for env in ("prod", "staging", "test"):
            expansions.add(f"{token}-{env}")
        for q in ("secure", "internal", "backend"):
            expansions.add(f"{token}-{q}")

    return sorted(expansions)


