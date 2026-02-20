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
- Heurísticas sector-aware (IT, Finance, Health, Telco, Gov, Edu, OT)
- Para uso em enterprise e académicos
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

VERSIONS = ["v1", "v2", "v3", "v1alpha", "v1beta"]

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

API_LIKE_TOKENS = {"api", "apis", "rest", "graphql", "service", "services"}

MANAGEMENT_TOKENS = {
    "admin", "portal", "dashboard", "console", "panel",
    "erp", "crm", "sap", "s4", "hana", "odoo", "servicenow", "jira", "confluence",
    "auth", "login", "sso", "iam", "identity", "keycloak", "okta",
    "grafana", "prometheus", "kibana", "elastic",
    "zabbix", "nagios", "git", "gitlab", "jenkins", "ci", "cd",
    "vpn", "proxy", "firewall", "fw",
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
    "election", "voting", "internal", "securegov", "prod-gov"
}

# -------------------------------------------------------------------
# EDUCATION
# -------------------------------------------------------------------

EDU_TOKENS = {"campus", "student", "teacher", "staff", "moodle", "lms"}

# -------------------------------------------------------------------
# E-COMMERCE / RETAIL
# -------------------------------------------------------------------

ECOMMERCE_TOKENS = {
    "shop", "store", "cart", "checkout", "orders",
    "catalog", "inventory", "warehouse", "payment",
    "customer", "returns", "refund", "api"
}

# -------------------------------------------------------------------
# Expansion engine
# -------------------------------------------------------------------

def expand_weighted(token: str) -> list[tuple[str, float]]:
    """
    Expande um token com pesos heurísticos (0.0 – 1.0)
    """
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

    # 10. Education
    if token in EDU_TOKENS:
        for env in ("prod", "test"):
            add(f"{token}-{env}", 0.85)
        for q in ("internal", "academic", "campus"):
            add(f"{token}-{q}", 0.83)

    # 11. E-commerce
    if token in ECOMMERCE_TOKENS:
        for env in ("prod", "staging", "test"):
            add(f"{token}-{env}", 0.90)
        for q in ("secure", "internal", "backend", "payments"):
            add(f"{token}-{q}", 0.88)

    return sorted(expansions.items(), key=lambda x: x[1], reverse=True)

#
# # --------------------------------------------------------------------------------------------------
# # TugaRecon
# # Author: Skynet0x01 2020-2026
# # GitHub: https://github.com/skynet0x01/tugarecon
# # License: GNU GPLv3
# # Model: models/IA/heuristics.py
# # Patent Restriction Notice:
# # No patents may be claimed or enforced on this software or any derivative.
# # Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# # --------------------------------------------------------------------------------------------------
#
# """
#     Heuristic tsoken expansion engine
#     Extended with multi-sector intelligence.
#
#     This module is intentionally conservative:
#     - No combinatorial explosions
#     - Deterministic output
#     - Sector-aware heuristics (IT, Finance, Health, Telco, Gov, Edu, OT)
#     - Designed for enterprise and academic reconnaissance
# """
#
# # -------------------------------------------------------------------
# # Generic domain knowledge
# # -------------------------------------------------------------------
#
# ENVIRONMENTS = [
#     "dev", "test", "testing",
#     "qa", "uat",
#     "stage", "staging",
#     "preprod", "pre-prod",
#     "prod", "production",
#     "lab", "sandbox",
# ]
#
# VERSIONS = [
#     "v1", "v2", "v3",
#     "v1alpha", "v1beta",
# ]
#
# QUALIFIERS = [
#     "internal", "private", "secure",
#     "public", "backend", "frontend",
#     "admin", "staff", "corp",
#     "intranet", "vpn",
#     "legacy", "old", "new",
# ]
#
# # -------------------------------------------------------------------
# # Semantic categories (IT / Enterprise)
# # -------------------------------------------------------------------
#
# API_LIKE_TOKENS = {
#     "api", "apis", "rest", "graphql",
#     "service", "services",
# }
#
# MANAGEMENT_TOKENS = {
#     "admin", "portal", "dashboard", "console", "panel",
#     "erp", "crm", "sap", "s4", "hana", "odoo",
#     "servicenow", "snow", "jira", "confluence",
#     "auth", "login", "sso", "iam", "identity",
#     "keycloak", "okta",
#     "grafana", "prometheus", "kibana", "elastic",
#     "zabbix", "nagios",
#     "git", "gitlab", "jenkins", "ci", "cd",
#     "vpn", "proxy", "firewall", "fw",
# }
#
# # -------------------------------------------------------------------
# # SCADA / ICS – Core domains
# # -------------------------------------------------------------------
#
# SCADA_CONTROL_TOKENS = {
#     # Controladores
#     "plc", "rtu", "ied", "hmi", "pac", "dcu", "mtu",
#     "controller", "logic", "safetycontroller",
#     "failsafe", "redundant",
#
#     # Protocolos industriais
#     "modbus", "modbus-tcp",
#     "dnp3", "iec101", "iec104",
#     "bacnet", "opc", "opcua",
#     "profinet", "ethernetip",
#     "canbus", "hart",
#
#     # Arquitetura ICS
#     "field", "fieldbus",
#     "node", "station",
#     "controlroom",
#     "master", "slave",
#     "primary", "secondary",
#
#     # Energia e proteção
#     "relay", "protection",
#     "breaker", "switchgear",
#     "feeder", "bay"
# }
#
# SCADA_MONITOR_TOKENS = {
#     "scada", "supervisory",
#     "monitor", "view", "overview",
#     "operator", "cockpit",
#     "dashboard", "console",
#
#     # Historiadores industriais
#     "historian", "processhistorian",
#     "history", "log", "archive",
#     "trend", "trending",
#
#     # Bases de dados OT
#     "sql-scada", "db-ics",
#     "timeseries", "pi-server",
#     "osi-pi",
#
#     # Gestão energética
#     "ems", "dms", "bms",
#     "energy-mgmt", "power-mgmt",
#
#     # Alarmística
#     "alarm", "alerts",
#     "event", "incidents"
# }
#
# SCADA_REMOTE_TOKENS = {
#     "remote-scada", "vpn-ot",
#     "eng", "engineering",
#     "engstation", "eng-workstation",
#     "config", "setup",
#     "admin-scada",
#     "maintenance", "service",
#     "support-ics", "portal-ot",
#     "remote-access",
#     "jumpserver", "jumphost",
#     "citrix-ot",
#     "vendor-access",
#     "thirdparty",
#     "diagnostics"
# }
#
# SCADA_ENERGY_TOKENS = {
#     "grid", "smartgrid",
#     "substation", "switchyard",
#     "solar", "wind",
#     "hydro", "thermal",
#     "meter", "smartmeter",
#     "transformer",
#     "feeder", "distribution",
#     "transmission",
#     "load", "generation",
#     "powerplant",
#     "turbine", "generator"
# }
#
# SCADA_WATER_TOKENS = {
#     "pump", "pumpingstation",
#     "well", "borehole",
#     "treatment", "watertreatment",
#     "wastewater", "sewage",
#     "flow", "flowmeter",
#     "tank", "valve",
#     "reservoir", "basin",
#     "chlorination",
#     "filtration",
#     "pressure",
#     "pipeline"
# }
#
# SCADA_MANUFACTURING_TOKENS = {
#     "plant", "factory",
#     "production", "line1", "line2",
#     "assembly", "cell",
#     "mes", "erp-plant",
#     "robot", "robotics",
#     "cobot",
#     "cnc",
#     "packaging",
#     "conveyor",
#     "molding",
#     "press",
#     "quality", "qa",
#     "batch"
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
#     "ach",
#     "atm", "terminal",
#     "billing", "invoice",
#     "card", "cards", "visa", "mastercard",
#     "fraud", "aml", "kyc",
#     "treasury", "trading", "broker",
#     "risk", "compliance",
#     "ledger",
#
#     # Core banking & sistemas principais
#     "banking", "corebank", "core-banking", "core", "ledger",
#     "accounts", "accounting", "clearing", "settlement",
#     "treasury", "liquidity", "recon", "reconciliation",
#
#     # Pagamentos
#     "payments", "payment", "pay", "payapi",
#     "gateway", "pg", "psp",
#     "pos", "acquirer", "issuer",
#     "instantpay", "rtp", "fasterpayments",
#     "openbanking", "open-banking",
#
#     # Redes e standards financeiros
#     "swift", "sepa", "iban", "bic",
#     "visa", "mastercard", "amex",
#     "pci", "pci-dss",
#
#     # APIs modernas
#     "api-payments", "api-banking",
#     "sandbox", "partnerapi", "externalapi",
#     "internalapi", "mobileapi",
#
#     # Autenticação e segurança
#     "authbank", "securebank",
#     "2fa", "mfa", "sso",
#     "token", "oauth", "oidc",
#     "fraud", "antifraud", "risk",
#     "kyc", "aml", "compliance",
#     "monitoring", "audit",
#
#     # Ambientes produtivos e críticos
#     "prod-banking", "prod-payments",
#     "dr", "disasterrecovery",
#     "ha", "highavailability",
#
#     # Canais digitais
#     "ebanking", "homebanking",
#     "mobilebank", "internetbank",
#     "appbank", "wallet",
#
#     # Infra típica fintech
#     "fintech", "lending", "loans",
#     "credit", "debit", "cards",
#     "issuerapi", "acquirerapi",
#     "settlementapi"
# }
#
# # -------------------------------------------------------------------
# # HEALTH
# # -------------------------------------------------------------------
#
# HEALTH_TOKENS = {
#     "his", "ris", "pacs",
#     "ehr", "emr",
#     "hl7", "fhir", "dicom",
#     "radiology", "lab", "lis",
#     "pharmacy", "prescription",
#     "patient", "clinical",
#     "imaging", "scan",
#     "billing-health",
#
#     # Sistemas clínicos centrais
#     "his", "ehr", "emr",
#     "clinical", "clinic",
#     "patient", "patients",
#     "record", "records",
#     "healthrecord",
#
#     # Imagiologia
#     "pacs", "dicom",
#     "radiology", "radiologyapi",
#     "imaging", "ris",
#
#     # Laboratório
#     "lis", "lab", "laboratory",
#     "pathology", "microbiology",
#     "bloodbank",
#
#     # Sistemas hospitalares administrativos
#     "admission", "adt",
#     "billing", "claims",
#     "insurance", "payer",
#     "revenuecycle",
#
#     # Prescrição e farmácia
#     "pharmacy", "rx",
#     "eprescription", "erx",
#     "medication", "medadmin",
#
#     # Telemedicina e portais
#     "telemed", "telemedicine",
#     "portal", "patientportal",
#     "myhealth", "myehr",
#     "appointment", "scheduling",
#
#     # Interoperabilidade
#     "hl7", "fhir",
#     "interop", "integration",
#     "hie",  # Health Information Exchange
#
#     # Dispositivos médicos e IoT clínico
#     "biomed", "device",
#     "monitoring", "vitals",
#     "icu", "ward",
#
#     # Ambientes sensíveis
#     "prod-clinical",
#     "securehealth",
#     "hipaa", "gdprhealth",
#     "compliance",
#     "audit",
#
#     # Especialidades
#     "oncology", "cardiology",
#     "dermatology", "neurology",
#     "surgery", "er", "emergency"
# }
#
# # -------------------------------------------------------------------
# # TELCO
# # -------------------------------------------------------------------
#
# TELCO_TOKENS = {
#     "core-net", "bss", "oss",
#     "hlr", "hss", "ims",
#     "msc", "sgw", "pgw",
#     "cdr", "billing-telco",
#     "provisioning", "radius",
#     "voip", "sip",
#     "lte", "5g", "nr",
#
#     # Business & Operations Support Systems
#     "bss", "oss",
#     "crm", "billing", "charging",
#     "ocs", "ofcs",
#     "provisioning", "mediation",
#     "rating",
#
#     # Core móvel (2G/3G/4G)
#     "hlr", "hss",
#     "msc", "mgw",
#     "sgsn", "ggsn",
#     "mme", "pcrf",
#     "evolvedpacketcore", "epc",
#
#     # 4G / LTE
#     "lte", "enodeb",
#     "volte", "diameter",
#     "s1ap",
#
#     # 5G Core
#     "5g", "5gc",
#     "amf", "smf", "upf",
#     "nrf", "ausf", "udm",
#     "network-slicing",
#
#     # IMS (VoIP core)
#     "ims", "pcscf",
#     "icscf", "scscf",
#     "sip", "voip",
#
#     # DNS e rede IP
#     "dns-telco", "bgp",
#     "peering", "transit",
#     "mpls", "ipcore",
#     "backbone",
#
#     # Fixed broadband
#     "olt", "bras",
#     "bnngw", "fiber",
#     "ftth", "xgspon",
#
#     # Infraestrutura física e rádio
#     "ran", "core", "radio",
#     "nodeb", "gnodeb",
#     "tower", "site",
#
#     # Segurança e lawful intercept
#     "li", "lawful",
#     "securitycore",
#     "firewallcore",
#
#     # IoT e serviços digitais
#     "iot", "m2m",
#     "mvno", "roaming",
#     "smsc", "mmsc",
#     "usap", "usf",
#
#     # Ambientes críticos
#     "prod-core",
#     "prod-ims",
#     "dr", "ha",
#     "noc", "soc"
# }
#
# # -------------------------------------------------------------------
# # GOVERNMENT
# # -------------------------------------------------------------------
#
# GOV_TOKENS = {
#     "citizen", "portal-cidadao",
#     "tax", "financas",
#     "justice", "court",
#     "police", "psp", "gnr",
#     "customs", "immigration",
#     "eproc", "procurement",
#     "registry", "civil",
#     "election", "voting",
#
# # Cidadão e portais públicos
#     "citizen", "portal", "govportal",
#     "servicos", "servicosonline",
#     "eportugal", "egov",
#     "balcaounico", "one-stop",
#     "atendimento",
#
#     # Fiscalidade e finanças públicas
#     "tax", "financas", "tributario",
#     "revenue", "customs",
#     "alfandega", "vat",
#     "iva", "irs", "irc",
#     "impostos", "contribuinte",
#     "at", "autoridadetributaria",
#
#     # Registos e identificação
#     "registry", "registo",
#     "civil", "predial",
#     "automovel",
#     "notariado", "notary",
#     "id", "identity",
#     "passport", "cartao",
#     "nif", "nid",
#     "population",
#
#     # Justiça e tribunais
#     "justice", "tribunal",
#     "courts", "judicial",
#     "prosecutor", "mp",
#     "police", "interior",
#     "criminal", "penal",
#     "citius",
#
#     # Segurança social e apoio
#     "social", "segurancasocial",
#     "benefits", "subsidio",
#     "pension", "retirement",
#     "unemployment",
#
#     # Saúde pública
#     "sns", "saudepublica",
#     "vaccination", "vacinas",
#     "epidemiology",
#
#     # Educação pública
#     "education", "edu",
#     "escola", "universidade",
#     "scholarship",
# QUALIFIERS
#     # Infraestrutura crítica
#     "internal", "intranet",
#     "prod-gov",
#     "securegov",
#     "classified",
#     "defense", "military",
#     "armedforces",
#
#     # Transparência e dados abertos
#     "opendata", "dadosabertos",
#     "transparency",
#     "publicrecords",
#
#     # Eleições
#     "election", "voting",
#     "recenseamento"
# }
#
# # -------------------------------------------------------------------
# # EDUCATION
# # -------------------------------------------------------------------
#
# EDU_TOKENS = {
#     "campus", "student", "students",
#     "teacher", "staff",
#     "moodle", "lms",
#     "exam", "grades",
#     "library", "repo",
#     "admissions", "enroll",
#     "alumni",
# }
#
# # -------------------------------------------------------------------
# # E-COMMERCE / RETAIL
# # -------------------------------------------------------------------
#
# ECOMMERCE_TOKENS = {
#     "shop", "store",
#     "cart", "checkout",
#     "orders", "order",
#     "catalog", "inventory",
#     "warehouse", "fulfillment",
#     "payment", "gateway",
#     "customer", "crm-retail",
#     "returns", "refund",
#
#     # Núcleo transacional
#     "checkout", "payment", "payments",
#     "orders", "order", "cart",
#     "basket", "purchase",
#     "transaction",
#
#     # Conta e identidade
#     "account", "accounts",
#     "customer", "customers",
#     "profile", "login",
#     "auth", "sso",
#     "register", "signup",
#
#     # Catálogo e produto
#     "catalog", "product",
#     "products", "inventory",
#     "stock", "pricing",
#     "search", "recommendation",
#
#     # Marketplace
#     "seller", "vendor",
#     "merchant", "marketplace",
#     "affiliate",
#
#     # Fulfillment e logística
#     "shipping", "delivery",
#     "fulfillment", "warehouse",
#     "returns", "tracking",
#
#     # Pagamentos avançados
#     "gateway", "psp",
#     "3ds", "fraud",
#     "risk", "chargeback",
#     "wallet", "giftcard",
#
#     # APIs modernas
#     "api", "store-api",
#     "graphql", "rest",
#     "webhooks", "integration",
#
#     # Frontend / canais
#     "shop", "store",
#     "mobile", "app",
#     "mcommerce",
#
#     # Marketing e growth
#     "promo", "coupon",
#     "discount", "campaign",
#     "ads", "analytics",
#
#     # Ambientes críticos
#     "prod-shop",
#     "securepay",
#     "live", "production",
#     "dr", "ha"
# }
#
# # -------------------------------------------------------------------
# # Expansion engine
# # -------------------------------------------------------------------
# def expand_weighted(token: str) -> list[tuple[str, float]]:
#     """
#     Expande um token e associa um peso heurístico (0.0 – 1.0).
#
#     Filosofia:
#     - Peso alto → altamente provável em ambientes reais
#     - Peso médio → comum mas dependente de maturidade da organização
#     - Peso baixo → plausível mas menos frequente
#     - Determinístico
#     """
#
#     token = token.lower()
#     expansions: dict[str, float] = {}
#
#     def add(candidate: str, weight: float):
#         # Mantém sempre o maior peso caso exista duplicação
#         if candidate not in expansions or expansions[candidate] < weight:
#             expansions[candidate] = weight
#
#     # ------------------------------------------------------------------
#     # 1. Ambientes universais
#     # ------------------------------------------------------------------
#
#     for env in ENVIRONMENTS:
#         if env in ("prod", "production"):
#             add(f"{token}-{env}", 0.95)
#         elif env in ("dev", "test", "qa", "uat"):
#             add(f"{token}-{env}", 0.85)
#         else:
#             add(f"{token}-{env}", 0.70)
#
#     # ------------------------------------------------------------------
#     # 2. Qualificadores globais
#     # ------------------------------------------------------------------
#
#     for qualifier in QUALIFIERS:
#         if qualifier in ("internal", "admin", "secure"):
#             add(f"{token}-{qualifier}", 0.80)
#         else:
#             add(f"{token}-{qualifier}", 0.65)
#
#     # ------------------------------------------------------------------
#     # 3. API / Versionamento
#     # ------------------------------------------------------------------
#
#     if token in API_LIKE_TOKENS:
#         for version in VERSIONS:
#             add(f"{token}-{version}", 0.88)
#
#             for env in ENVIRONMENTS:
#                 if env in ("prod", "production"):
#                     add(f"{token}-{version}-{env}", 0.82)
#                 else:
#                     add(f"{token}-{version}-{env}", 0.72)
#
#     # ------------------------------------------------------------------
#     # 4. Management / Admin Systems
#     # ------------------------------------------------------------------
#
#     if token in MANAGEMENT_TOKENS:
#         for env in ("dev", "qa", "uat", "prod"):
#             add(f"{token}-{env}", 0.92)
#
#         for q in ("admin", "internal", "corp", "secure"):
#             add(f"{token}-{q}", 0.90)
#
#     # ------------------------------------------------------------------
#     # 5. SCADA / OT (aqui o risco real começa)
#     # ------------------------------------------------------------------
#
#     if token in SCADA_TOKENS:
#         for env in ("prod", "uat", "qa"):
#             add(f"{token}-{env}", 0.93)
#
#         for q in ("control", "operator", "internal", "eng"):
#             add(f"{token}-{q}", 0.91)
#
#     if token in SCADA_ENERGY_TOKENS:
#         for suffix in ("grid", "substation", "control", "dispatch"):
#             add(f"{token}-{suffix}", 0.89)
#
#     if token in SCADA_WATER_TOKENS:
#         for suffix in ("plant", "control", "monitor", "treatment"):
#             add(f"{token}-{suffix}", 0.88)
#
#     if token in SCADA_MANUFACTURING_TOKENS:
#         for suffix in ("line", "cell", "control", "mes", "robot"):
#             add(f"{token}-{suffix}", 0.87)
#
#     # ------------------------------------------------------------------
#     # 6. Finance (muito padronizado)
#     # ------------------------------------------------------------------
#
#     if token in FINANCE_TOKENS:
#         for env in ("prod", "uat", "qa", "dr"):
#             add(f"{token}-{env}", 0.94)
#
#         for q in ("secure", "internal", "core", "settlement"):
#             add(f"{token}-{q}", 0.91)
#
#     # ------------------------------------------------------------------
#     # 7. Health
#     # ------------------------------------------------------------------
#
#     if token in HEALTH_TOKENS:
#         for env in ("prod", "test", "dr"):
#             add(f"{token}-{env}", 0.93)
#
#         for q in ("internal", "secure", "clinical", "patient"):
#             add(f"{token}-{q}", 0.90)
#
#     # ------------------------------------------------------------------
#     # 8. Telco
#     # ------------------------------------------------------------------
#
#     if token in TELCO_TOKENS:
#         for env in ("prod", "lab", "test"):
#             add(f"{token}-{env}", 0.92)
#
#         for q in ("internal", "net", "core", "edge"):
#             add(f"{token}-{q}", 0.89)
#
#     # ------------------------------------------------------------------
#     # 9. Government
#     # ------------------------------------------------------------------
#
#     if token in GOV_TOKENS:
#         for env in ("prod", "uat", "dr"):
#             add(f"{token}-{env}", 0.94)
#
#         for q in ("public", "internal", "secure", "gov"):
#             add(f"{token}-{q}", 0.91)
#
#     # ------------------------------------------------------------------
#     # 10. Education
#     # ------------------------------------------------------------------
#
#     if token in EDU_TOKENS:
#         for env in ("prod", "test"):
#             add(f"{token}-{env}", 0.85)
#
#         for q in ("internal", "academic", "campus"):
#             add(f"{token}-{q}", 0.83)
#
#     # ------------------------------------------------------------------
#     # 11. E-commerce
#     # ------------------------------------------------------------------
#
#     if token in ECOMMERCE_TOKENS:
#         for env in ("prod", "staging", "test"):
#             add(f"{token}-{env}", 0.90)
#
#         for q in ("secure", "internal", "backend", "payments"):
#             add(f"{token}-{q}", 0.88)
#
#     # ------------------------------------------------------------------
#     # Output determinístico ordenado por peso descendente
#     # ------------------------------------------------------------------
#
#     return sorted(expansions.items(), key=lambda x: x[1], reverse=True)
