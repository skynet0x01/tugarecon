# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Model: modules/IA/heuristics.py
# --------------------------------------------------------------------------------------------------

"""
Heuristic token expansion engine
Extended with multi-sector intelligence.

Este módulo é conservador:
- Sem explosões combinatórias
- Saída determinística
- Heurísticas sector-aware (IT, Finance, Health, Telco, Gov, Edu, OT, Security)
- Para uso em enterprise e académicos
"""

# -------------------------------------------------------------------
# Generic domain knowledge
# -------------------------------------------------------------------
ENVIRONMENTS = [
    "dev", "devel", "development",
    "test", "testing", "tst",
    "qa", "uat",
    "stage", "staging",
    "preprod", "pre-prod", "preproduction",
    "prod", "production",
    "dr", "drp", "disaster-recovery",
    "backup", "bkp",
    "lab", "sandbox",
    "pilot", "poc",
    "demo",
    "int", "integration",
    "perf", "performance",
    "load", "stress",
    "training",
    "acceptance",
]

VERSIONS = [
    "v1", "v2", "v3", "v4",
    "v01", "v02",
    "v1alpha", "v1beta",
    "alpha", "beta", "rc",
    "release", "stable",
    "legacy",
    "2023", "2024", "2025", "2026",
]

QUALIFIERS = [
    "internal", "private", "secure",
    "public", "external",
    "backend", "frontend",
    "admin", "staff", "corp",
    "intranet", "vpn",
    "legacy", "old", "new",
    "edge", "core",
    "dmz",
    "gateway", "gw",
    "auth", "login", "sso",
    "api", "rest",
    "cdn",
    "static",
    "media",
    "files",
    "storage",
    "db", "database",
    "cache", "redis",
    "mq", "queue",
    "search",
    "monitor", "monitoring",
    "metrics",
    "logs", "logging",
    "backup",
    "replica",
    "primary", "secondary",
    "cluster",
    "node",
]

# -------------------------------------------------------------------
# Semantic categories (IT / Enterprise)
# -------------------------------------------------------------------

API_LIKE_TOKENS = {"api", "apis", "rest", "graphql", "service", "services"}

MANAGEMENT_TOKENS = {
    "admin", "portal", "dashboard", "console", "panel",
    "erp", "crm", "sap", "s4", "hana", "odoo",
    "servicenow", "jira", "confluence",
    "auth", "login", "sso", "iam", "identity",
    "keycloak", "okta", "auth0",
    "git", "gitlab", "github", "gitea",
    "jenkins", "ci", "cd",
    "runner", "harbor",
    "artifactory", "nexus",
    "sonarqube",
    "k8s", "kubernetes",
    "rancher",
    "argocd",
    "argo",
    "istio",
    "traefik",
    "grafana", "prometheus",
    "kibana", "elastic",
    "logstash",
    "loki",
    "zabbix", "nagios",
    "cloud", "aws", "azure", "gcp",
    "openshift",
    "vpn", "proxy",
    "firewall", "fw",
    "fortigate", "paloalto",
    "citrix", "rdp",
    "guacamole",
}

CLOUD_NATIVE_TOKENS = {
    "storage", "blob",
    "cdn", "assets",
    "files", "uploads",
    "media",
    "static",
    "app",
    "web",
    "api",
    "lambda",
    "function",
    "serverless",
    "gateway",
    "edge",
    "lb", "loadbalancer",
    "elb", "alb",
    "waf",
}

# -------------------------------------------------------------------
# SCADA / ICS – Core domains
# -------------------------------------------------------------------

SCADA_CONTROL_TOKENS = {
    "plc", "rtu", "ied", "hmi", "pac", "dcu", "mtu",
    "controller", "logic", "safetycontroller",
    "failsafe", "redundant",
    "modbus", "modbus-tcp", "dnp3", "iec101", "iec104",
    "bacnet", "opc", "opcua", "profinet", "ethernetip",
    "canbus", "hart",
    "field", "fieldbus", "node", "station", "controlroom",
    "master", "slave", "primary", "secondary",
    "relay", "protection", "breaker", "switchgear",
    "feeder", "bay"
}

SCADA_MONITOR_TOKENS = {
    "scada", "supervisory", "monitor", "view", "overview",
    "operator", "cockpit", "dashboard", "console",
    "historian", "processhistorian", "history", "log", "archive",
    "trend", "trending", "sql-scada", "db-ics",
    "timeseries", "pi-server", "osi-pi",
    "ems", "dms", "bms", "energy-mgmt", "power-mgmt",
    "alarm", "alerts", "event", "incidents"
}

SCADA_REMOTE_TOKENS = {
    "remote-scada", "vpn-ot", "eng", "engineering",
    "engstation", "eng-workstation", "config", "setup",
    "admin-scada", "maintenance", "service",
    "support-ics", "portal-ot", "remote-access",
    "jumpserver", "jumphost", "citrix-ot",
    "vendor-access", "thirdparty", "diagnostics"
}

SCADA_ENERGY_TOKENS = {
    "grid", "smartgrid", "substation", "switchyard",
    "solar", "wind", "hydro", "thermal",
    "meter", "smartmeter", "transformer",
    "feeder", "distribution", "transmission",
    "load", "generation", "powerplant",
    "turbine", "generator"
}

SCADA_WATER_TOKENS = {
    "pump", "pumpingstation", "well", "borehole",
    "treatment", "watertreatment", "wastewater", "sewage",
    "flow", "flowmeter", "tank", "valve", "reservoir", "basin",
    "chlorination", "filtration", "pressure", "pipeline"
}

SCADA_MANUFACTURING_TOKENS = {
    "plant", "factory", "production", "line1", "line2",
    "assembly", "cell", "mes", "erp-plant", "robot",
    "robotics", "cobot", "cnc", "packaging",
    "conveyor", "molding", "press", "quality", "qa", "batch"
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
    "ach", "atm", "billing", "invoice", "card", "cards",
    "visa", "mastercard", "fraud", "aml", "kyc",
    "treasury", "trading", "broker", "risk", "compliance",
    "ledger", "banking", "corebank", "accounts",
    "payments", "openbanking", "api-payments"
}

# -------------------------------------------------------------------
# HEALTH
# -------------------------------------------------------------------

HEALTH_TOKENS = {
    "his", "ris", "pacs", "ehr", "emr",
    "hl7", "fhir", "dicom",
    "radiology", "lab", "lis", "pharmacy", "patient",
    "clinical", "appointment", "telemed", "securehealth"
}

# -------------------------------------------------------------------
# TELCO
# -------------------------------------------------------------------

TELCO_TOKENS = {
    "core-net", "bss", "oss", "hlr", "hss", "ims",
    "msc", "sgw", "pgw", "cdr", "billing-telco",
    "radius", "voip", "sip", "lte", "5g", "nr"
}

# -------------------------------------------------------------------
# GOVERNMENT
# -------------------------------------------------------------------

GOV_TOKENS = {
    "citizen", "portal-cidadao", "tax", "financas",
    "justice", "court", "police", "psp", "gnr",
    "customs", "immigration", "registry", "civil",
    "election", "voting", "internal", "securegov", "prod-gov",
    "ministry", "secretariat", "department", "cabinet",
    "parliament", "congress", "senate"
}

# -------------------------------------------------------------------
# MILITARY
# -------------------------------------------------------------------

MILITARY_TOKENS = {
    "army", "navy", "airforce", "marines", "specialforces",
    "command", "base", "arsenal", "brigade", "division",
    "battalion", "platoon", "regiment",
    "cyberdefense", "intel", "ops", "hq"
}

# -------------------------------------------------------------------
# SECURITY / INTELLIGENCE
# -------------------------------------------------------------------

SECURITY_TOKENS = {
    "nsa", "cia", "fbi", "mi6", "gchq", "dhs", "dod",
    "homeland", "intel", "recon", "surveillance", "espionage",
    "soc", "secops", "cyber", "firewall", "ids", "ips",
    "threat", "threatintel", "redteam", "blueteam", "pentest",
    "forensics", "incident", "ir", "malware", "sandbox", "honey",
    "covert", "blackops", "sigint", "elint", "commint", "cyberdefense",
    "redcell", "bluecell", "vulnerability", "zero-day", "exploit",
}

# -------------------------------------------------------------------
# DEEP SECURITY / COVERT TECH
# -------------------------------------------------------------------

DEEPSEC_TOKENS = {
    # Inteligência SIGINT / ELINT
    "sigint", "elint", "commint", "signals", "intercept", "radio", "satcom",
    "telemetry", "recon", "espionage", "covert", "blackops", "redcell", "bluecell",

    # Cyber operations
    "cyberwarfare", "offensive", "defensive", "malware", "exploit", "zeroday", "vulnerability",
    "hacking", "pentest", "redteam", "blueteam", "soc", "forensics", "incident", "ir",

    # Drones / Robotics / ISR (Intelligence, Surveillance, Recon)
    "uav", "drone", "uas", "loitering", "surveillance-drone", "recon-drone",
    "robotics", "cobot", "autonomous", "ai-control", "remote-ops", "groundstation",

    # Satellite / Space Ops
    "satellite", "groundstation", "telemetry", "commsat", "spy-sat", "orbital", "payload",
    "sat-imagery", "radar", "synthetic-aperture", "remote-sensing",

    # Crypto / Secure Comms
    "crypto", "encryption", "cipher", "aes", "rsa", "elliptic", "keyexchange",
    "securechannel", "vpn", "tor", "onion", "mixnet", "obfuscation", "steganography"
}
# -------------------------------------------------------------------
# EDUCATION
# -------------------------------------------------------------------

EDU_TOKENS = {"campus", "student", "teacher", "staff", "moodle", "lms"}

# -------------------------------------------------------------------
# E-COMMERCE / RETAIL
# -------------------------------------------------------------------

ECOMMERCE_TOKENS = {
    "shop", "store",
    "cart", "checkout",
    "orders", "order",
    "catalog",
    "inventory",
    "warehouse",
    "payment", "payments",
    "stripe", "paypal",
    "customer", "customers",
    "returns", "refund",
    "shipping",
    "tracking",
    "affiliate",
    "promo",
    "discount",
}

# -------------------------------------------------------------------
# Expansion engine
# -------------------------------------------------------------------

def expand_weighted(token: str) -> list[tuple[str, float]]:
    token = token.lower()
    expansions: dict[str, float] = {}

    def add(candidate: str, weight: float):
        if candidate not in expansions or expansions[candidate] < weight:
            expansions[candidate] = weight

    # 1. Ambientes
    for env in ENVIRONMENTS:
        weight = 0.95 if env in ("prod", "production") else 0.85 if env in ("dev", "test", "qa", "uat") else 0.70
        add(f"{token}-{env}", weight)

    # 2. Qualificadores
    for q in QUALIFIERS:
        weight = 0.80 if q in ("internal", "admin", "secure") else 0.65
        add(f"{token}-{q}", weight)

    # 3. API / Versionamento
    if token in API_LIKE_TOKENS:
        for version in VERSIONS:
            add(f"{token}-{version}", 0.88)
            for env in ENVIRONMENTS:
                add(f"{token}-{version}-{env}", 0.82 if env in ("prod", "production") else 0.72)

    # 4. Management
    if token in MANAGEMENT_TOKENS:
        for env in ("dev", "qa", "uat", "prod"):
            add(f"{token}-{env}", 0.92)
        for q in ("admin", "internal", "corp", "secure"):
            add(f"{token}-{q}", 0.90)

    # 5. SCADA / OT
    if token in SCADA_TOKENS:
        for env in ("prod", "uat", "qa"):
            add(f"{token}-{env}", 0.93)
        for q in ("control", "operator", "internal", "eng"):
            add(f"{token}-{q}", 0.91)

    # 6. Finance
    if token in FINANCE_TOKENS:
        for env in ("prod", "uat", "qa", "dr"):
            add(f"{token}-{env}", 0.94)
        for q in ("secure", "internal", "core", "settlement"):
            add(f"{token}-{q}", 0.91)

    # 7. Health
    if token in HEALTH_TOKENS:
        for env in ("prod", "test", "dr"):
            add(f"{token}-{env}", 0.93)
        for q in ("internal", "secure", "clinical", "patient"):
            add(f"{token}-{q}", 0.90)

    # 8. Telco
    if token in TELCO_TOKENS:
        for env in ("prod", "lab", "test"):
            add(f"{token}-{env}", 0.92)
        for q in ("internal", "net", "core", "edge"):
            add(f"{token}-{q}", 0.89)

    # 9. Government
    if token in GOV_TOKENS:
        for env in ("prod", "uat", "dr"):
            add(f"{token}-{env}", 0.94)
        for q in ("public", "internal", "secure", "gov"):
            add(f"{token}-{q}", 0.91)

    # 10. Military
    if token in MILITARY_TOKENS:
        for env in ("prod", "uat", "dr", "lab"):
            add(f"{token}-{env}", 0.94)
        for q in ("internal", "secure", "hq", "ops"):
            add(f"{token}-{q}", 0.91)

    # 11. Security / Intelligence
    if token in SECURITY_TOKENS:
        for env in ("prod", "uat", "dr", "lab"):
            add(f"{token}-{env}", 0.94)
        for q in ("internal", "secure", "ops", "intel"):
            add(f"{token}-{q}", 0.91)

    # 12. Education
    if token in EDU_TOKENS:
        for env in ("prod", "test"):
            add(f"{token}-{env}", 0.85)
        for q in ("internal", "academic", "campus"):
            add(f"{token}-{q}", 0.83)

    # 13. E-commerce
    if token in ECOMMERCE_TOKENS:
        for env in ("prod", "staging", "test"):
            add(f"{token}-{env}", 0.90)
        for q in ("secure", "internal", "backend", "payments"):
            add(f"{token}-{q}", 0.88)

    # 14. Deep Security / Covert Tech
    if token in DEEPSEC_TOKENS:
        for env in ("prod", "uat", "dr", "lab"):
            add(f"{token}-{env}", 0.95)
        for q in ("internal", "secure", "ops", "intel"):
            add(f"{token}-{q}", 0.92)

    return sorted(expansions.items(), key=lambda x: x[1], reverse=True)
# # --------------------------------------------------------------------------------------------------
# # TugaRecon
# # Author: Skynet0x01 2020-2026
# # GitHub: https://github.com/skynet0x01/tugarecon
# # License: GNU GPLv3
# # Model: modules/IA/heuristics.py
# # --------------------------------------------------------------------------------------------------
#
# """
# Heuristic token expansion engine
# Extended with multi-sector intelligence.
#
# Este módulo é conservador:
# - Sem explosões combinatórias
# - Saída determinística
# - Heurísticas sector-aware (IT, Finance, Health, Telco, Gov, Edu, OT, Military)
# - Para uso em enterprise e académicos
# """
#
# # -------------------------------------------------------------------
# # Generic domain knowledge
# # -------------------------------------------------------------------
# ENVIRONMENTS = [
#     # Core
#     "dev", "devel", "development",
#     "test", "testing", "tst",
#     "qa", "uat",
#     "stage", "staging",
#     "preprod", "pre-prod", "preproduction",
#     "prod", "production",
#     "dr", "drp", "disaster-recovery",
#     "backup", "bkp",
#     "lab", "sandbox",
#     "pilot", "poc",
#     "demo",
#     "int", "integration",
#     "perf", "performance",
#     "load", "stress",
#     "training",
#     "acceptance",
# ]
#
# VERSIONS = [
#     "v1", "v2", "v3", "v4",
#     "v01", "v02",
#     "v1alpha", "v1beta",
#     "alpha", "beta", "rc",
#     "release", "stable",
#     "legacy",
#     "2023", "2024", "2025", "2026",
# ]
#
# QUALIFIERS = [
#     "internal", "private", "secure",
#     "public", "external",
#     "backend", "frontend",
#     "admin", "staff", "corp",
#     "intranet", "vpn",
#     "legacy", "old", "new",
#     "edge", "core",
#     "dmz",
#     "gateway", "gw",
#     "auth", "login", "sso",
#     "api", "rest",
#     "cdn",
#     "static",
#     "media",
#     "files",
#     "storage",
#     "db", "database",
#     "cache", "redis",
#     "mq", "queue",
#     "search",
#     "monitor", "monitoring",
#     "metrics",
#     "logs", "logging",
#     "backup",
#     "replica",
#     "primary", "secondary",
#     "cluster",
#     "node",
# ]
#
# # -------------------------------------------------------------------
# # Semantic categories (IT / Enterprise)
# # -------------------------------------------------------------------
#
# API_LIKE_TOKENS = {"api", "apis", "rest", "graphql", "service", "services"}
#
# MANAGEMENT_TOKENS = {
#     # Core enterprise
#     "admin", "portal", "dashboard", "console", "panel",
#     "erp", "crm", "sap", "s4", "hana", "odoo",
#     "servicenow", "jira", "confluence",
#     "auth", "login", "sso", "iam", "identity",
#     "keycloak", "okta", "auth0",
#
#     # DevOps / CI/CD
#     "git", "gitlab", "github", "gitea",
#     "jenkins", "ci", "cd",
#     "runner", "harbor",
#     "artifactory", "nexus",
#     "sonarqube",
#
#     # Containers / Kubernetes
#     "k8s", "kubernetes",
#     "rancher",
#     "argocd",
#     "argo",
#     "istio",
#     "traefik",
#
#     # Observability
#     "grafana", "prometheus",
#     "kibana", "elastic",
#     "logstash",
#     "loki",
#     "zabbix", "nagios",
#
#     # Cloud panels
#     "cloud", "aws", "azure", "gcp",
#     "openshift",
#
#     # Remote access infra
#     "vpn", "proxy",
#     "firewall", "fw",
#     "fortigate", "paloalto",
#     "citrix", "rdp",
#     "guacamole",
# }
#
# CLOUD_NATIVE_TOKENS = {
#     "storage", "blob",
#     "cdn", "assets",
#     "files", "uploads",
#     "media",
#     "static",
#     "app",
#     "web",
#     "api",
#     "lambda",
#     "function",
#     "serverless",
#     "gateway",
#     "edge",
#     "lb", "loadbalancer",
#     "elb", "alb",
#     "waf",
# }
#
# # -------------------------------------------------------------------
# # SCADA / ICS – Core domains
# # -------------------------------------------------------------------
#
# SCADA_CONTROL_TOKENS = {
#     "plc", "rtu", "ied", "hmi", "pac", "dcu", "mtu",
#     "controller", "logic", "safetycontroller",
#     "failsafe", "redundant",
#     "modbus", "modbus-tcp", "dnp3", "iec101", "iec104",
#     "bacnet", "opc", "opcua", "profinet", "ethernetip",
#     "canbus", "hart",
#     "field", "fieldbus", "node", "station", "controlroom",
#     "master", "slave", "primary", "secondary",
#     "relay", "protection", "breaker", "switchgear",
#     "feeder", "bay"
# }
#
# SCADA_MONITOR_TOKENS = {
#     "scada", "supervisory", "monitor", "view", "overview",
#     "operator", "cockpit", "dashboard", "console",
#     "historian", "processhistorian", "history", "log", "archive",
#     "trend", "trending", "sql-scada", "db-ics",
#     "timeseries", "pi-server", "osi-pi",
#     "ems", "dms", "bms", "energy-mgmt", "power-mgmt",
#     "alarm", "alerts", "event", "incidents"
# }
#
# SCADA_REMOTE_TOKENS = {
#     "remote-scada", "vpn-ot", "eng", "engineering",
#     "engstation", "eng-workstation", "config", "setup",
#     "admin-scada", "maintenance", "service",
#     "support-ics", "portal-ot", "remote-access",
#     "jumpserver", "jumphost", "citrix-ot",
#     "vendor-access", "thirdparty", "diagnostics"
# }
#
# SCADA_ENERGY_TOKENS = {
#     "grid", "smartgrid", "substation", "switchyard",
#     "solar", "wind", "hydro", "thermal",
#     "meter", "smartmeter", "transformer",
#     "feeder", "distribution", "transmission",
#     "load", "generation", "powerplant",
#     "turbine", "generator"
# }
#
# SCADA_WATER_TOKENS = {
#     "pump", "pumpingstation", "well", "borehole",
#     "treatment", "watertreatment", "wastewater", "sewage",
#     "flow", "flowmeter", "tank", "valve", "reservoir", "basin",
#     "chlorination", "filtration", "pressure", "pipeline"
# }
#
# SCADA_MANUFACTURING_TOKENS = {
#     "plant", "factory", "production", "line1", "line2",
#     "assembly", "cell", "mes", "erp-plant", "robot",
#     "robotics", "cobot", "cnc", "packaging",
#     "conveyor", "molding", "press", "quality", "qa", "batch"
# }
#
# SCADA_TOKENS = (
#     SCADA_CONTROL_TOKENS
#     | SCADA_MONITOR_TOKENS
#     | SCADA_REMOTE_TOKENS
#     | SCADA_ENERGY_TOKENS
#     | SCADA_WATER_TOKENS
#     | SCADA_MANUFACTURING_TOKENS
# )
#
# # -------------------------------------------------------------------
# # FINANCE / BANKING
# # -------------------------------------------------------------------
#
# FINANCE_TOKENS = {
#     "ach", "atm", "billing", "invoice", "card", "cards",
#     "visa", "mastercard", "fraud", "aml", "kyc",
#     "treasury", "trading", "broker", "risk", "compliance",
#     "ledger", "banking", "corebank", "accounts",
#     "payments", "openbanking", "api-payments"
# }
#
# # -------------------------------------------------------------------
# # HEALTH
# # -------------------------------------------------------------------
#
# HEALTH_TOKENS = {
#     "his", "ris", "pacs", "ehr", "emr",
#     "hl7", "fhir", "dicom",
#     "radiology", "lab", "lis", "pharmacy", "patient",
#     "clinical", "appointment", "telemed", "securehealth"
# }
#
# # -------------------------------------------------------------------
# # TELCO
# # -------------------------------------------------------------------
#
# TELCO_TOKENS = {
#     "core-net", "bss", "oss", "hlr", "hss", "ims",
#     "msc", "sgw", "pgw", "cdr", "billing-telco",
#     "radius", "voip", "sip", "lte", "5g", "nr"
# }
#
# # -------------------------------------------------------------------
# # GOVERNMENT
# # -------------------------------------------------------------------
#
# GOV_TOKENS = {
#     "citizen", "portal-cidadao", "tax", "financas",
#     "justice", "court", "police", "psp", "gnr",
#     "customs", "immigration", "registry", "civil",
#     "election", "voting", "internal", "securegov", "prod-gov",
#     # Novos tokens
#     "legislation", "parliament", "govportal", "council",
#     "mayor", "ministry", "secretariat", "municipality",
#     "state", "federal", "cabinet", "minister", "department"
# }
#
# # -------------------------------------------------------------------
# # MILITARY / DEFENSE
# # -------------------------------------------------------------------
#
# MILITARY_TOKENS = {
#     "army", "navy", "airforce", "defense", "military",
#     "ops", "command", "hq", "barracks",
#     "cyberdefense", "intel", "specialforces",
#     "training", "drill", "arsenal", "fleet", "squadron"
# }
#
# # -------------------------------------------------------------------
# # SECURITY / INTELLIGENCE
# # -------------------------------------------------------------------
#
# SECURITY_TOKENS = {
#     # Intelligence / Spy Agencies
#     "nsa", "cia", "fbi", "mi6", "gchq", "dhs", "dod",
#     "homeland", "intel", "recon", "surveillance", "espionage",
#
#     # Cybersecurity / SOC
#     "soc", "secops", "cyber", "firewall", "ids", "ips",
#     "threat", "threatintel", "redteam", "blueteam", "pentest",
#     "forensics", "incident", "ir", "malware", "sandbox", "honey",
#
#     # Advanced / covert ops
#     "covert", "blackops", "sigint", "elint", "commint", "cyberdefense",
#     "redcell", "bluecell", "vulnerability", "zero-day", "exploit",
# }
#
# # -------------------------------------------------------------------
# # EDUCATION
# # -------------------------------------------------------------------
#
# EDU_TOKENS = {"campus", "student", "teacher", "staff", "moodle", "lms"}
#
# # -------------------------------------------------------------------
# # E-COMMERCE / RETAIL
# # -------------------------------------------------------------------
#
# ECOMMERCE_TOKENS = {
#     "shop", "store",
#     "cart", "checkout",
#     "orders", "order",
#     "catalog",
#     "inventory",
#     "warehouse",
#     "payment", "payments",
#     "stripe", "paypal",
#     "customer", "customers",
#     "returns", "refund",
#     "shipping",
#     "tracking",
#     "affiliate",
#     "promo",
#     "discount",
# }
#
# # -------------------------------------------------------------------
# # Expansion engine
# # -------------------------------------------------------------------
#
# def expand_weighted(token: str) -> list[tuple[str, float]]:
#     """
#     Expande um token com pesos heurísticos (0.0 – 1.0)
#     """
#     token = token.lower()
#     expansions: dict[str, float] = {}
#
#     def add(candidate: str, weight: float):
#         if candidate not in expansions or expansions[candidate] < weight:
#             expansions[candidate] = weight
#
#     # 1. Ambientes
#     for env in ENVIRONMENTS:
#         weight = 0.95 if env in ("prod", "production") else 0.85 if env in ("dev", "test", "qa", "uat") else 0.70
#         add(f"{token}-{env}", weight)
#
#     # 2. Qualificadores
#     for q in QUALIFIERS:
#         weight = 0.80 if q in ("internal", "admin", "secure") else 0.65
#         add(f"{token}-{q}", weight)
#
#     # 3. API / Versionamento
#     if token in API_LIKE_TOKENS:
#         for version in VERSIONS:
#             add(f"{token}-{version}", 0.88)
#             for env in ENVIRONMENTS:
#                 add(f"{token}-{version}-{env}", 0.82 if env in ("prod", "production") else 0.72)
#
#     # 4. Management
#     if token in MANAGEMENT_TOKENS:
#         for env in ("dev", "qa", "uat", "prod"):
#             add(f"{token}-{env}", 0.92)
#         for q in ("admin", "internal", "corp", "secure"):
#             add(f"{token}-{q}", 0.90)
#
#     # 5. SCADA / OT
#     if token in SCADA_TOKENS:
#         for env in ("prod", "uat", "qa"):
#             add(f"{token}-{env}", 0.93)
#         for q in ("control", "operator", "internal", "eng"):
#             add(f"{token}-{q}", 0.91)
#
#     # 6. Finance
#     if token in FINANCE_TOKENS:
#         for env in ("prod", "uat", "qa", "dr"):
#             add(f"{token}-{env}", 0.94)
#         for q in ("secure", "internal", "core", "settlement"):
#             add(f"{token}-{q}", 0.91)
#
#     # 7. Health
#     if token in HEALTH_TOKENS:
#         for env in ("prod", "test", "dr"):
#             add(f"{token}-{env}", 0.93)
#         for q in ("internal", "secure", "clinical", "patient"):
#             add(f"{token}-{q}", 0.90)
#
#     # 8. Telco
#     if token in TELCO_TOKENS:
#         for env in ("prod", "lab", "test"):
#             add(f"{token}-{env}", 0.92)
#         for q in ("internal", "net", "core", "edge"):
#             add(f"{token}-{q}", 0.89)
#
#     # 9. Government
#     if token in GOV_TOKENS:
#         for env in ("prod", "uat", "dr"):
#             add(f"{token}-{env}", 0.94)
#         for q in ("public", "internal", "secure", "gov"):
#             add(f"{token}-{q}", 0.91)
#
#     # 10. Military
#     if token in MILITARY_TOKENS:
#         for env in ("prod", "uat", "dr"):
#             add(f"{token}-{env}", 0.93)
#         for q in ("internal", "secure", "ops", "command"):
#             add(f"{token}-{q}", 0.90)
#
#     # 11. Education
#     if token in EDU_TOKENS:
#         for env in ("prod", "test"):
#             add(f"{token}-{env}", 0.85)
#         for q in ("internal", "academic", "campus"):
#             add(f"{token}-{q}", 0.83)
#
#     # 12. E-commerce
#     if token in ECOMMERCE_TOKENS:
#         for env in ("prod", "staging", "test"):
#             add(f"{token}-{env}", 0.90)
#         for q in ("secure", "internal", "backend", "payments"):
#             add(f"{token}-{q}", 0.88)
#
#     # 13. Security / Intelligence
#     if token in SECURITY_TOKENS:
#         for env in ("prod", "uat", "dr", "lab"):
#             add(f"{token}-{env}", 0.94)
#         for q in ("internal", "secure", "ops", "intel"):
#             add(f"{token}-{q}", 0.91)
#
#     return sorted(expansions.items(), key=lambda x: x[1], reverse=True)