# --------------------------------------------------------------------------------------------------
# TugaRecon - Impact Scoring (Enhanced)
# File: modules/IA/impact_score.py
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
from modules.IA.token_memory import update_token_stats

INFRASTRUCTURE_PATTERNS = {
    # Identity & Secrets
    "identity": {
        "patterns": ["auth", "sso", "iam", "login", "oauth", "oidc", "keycloak"],
        "tags": {"auth", "identity", "critical"}
    },
    "secrets": {
        "patterns": ["vault", "kms", "secrets", "keyvault", "keystore"],
        "tags": {"secrets", "infra", "critical"}
    },

    # Databases & Data
    "database": {
        "patterns": ["db", "database", "sql", "rds", "aurora", "postgres", "mysql", "mongo", "redis"],
        "tags": {"db", "data", "critical"}
    },

    # Storage
    "storage": {
        "patterns": ["s3", "bucket", "storage", "blob", "efs", "nfs", "backup", "archive"],
        "tags": {"storage", "data"}
    },

    # Network & Edge
    "network": {
        "patterns": ["gateway", "apigateway", "proxy", "lb", "loadbalancer", "edge", "waf"],
        "tags": {"network", "infra"}
    },

    # Containers & Orchestration
    "orchestration": {
        "patterns": ["k8s", "kubernetes", "eks", "aks", "gke", "cluster", "istio"],
        "tags": {"orchestration", "infra"}
    },

    # CI/CD
    "cicd": {
        "patterns": ["ci", "cd", "pipeline", "jenkins", "gitlab", "actions"],
        "tags": {"cicd", "infra"}
    },

    # Monitoring & Ops
    "observability": {
        "patterns": ["grafana", "prometheus", "kibana", "sentry", "monitor"],
        "tags": {"monitoring", "ops"}
    },

    # Admin & Control
    "admin": {
        "patterns": ["admin", "root", "control", "master", "console"],
        "tags": {"admin", "critical"}
    }
}

SCADA_TOKENS = {
    "plc", "rtu", "ied", "hmi", "pac", "dcu", "mtu",
    "controller", "logic", "gateway", "field", "node", "station",
    "modbus", "dnp3", "bacnet", "opc", "profinet",
    "scada", "supervisory", "monitor", "operator", "cockpit", "dashboard",
    "historian", "sql-scada", "db-ics",
    "ems", "dms", "bms",
    "remote-scada", "vpn-ot", "engineering", "admin-scada",
    "maintenance", "service", "portal-ot",
    "grid", "substation", "solar", "wind", "meter", "smartgrid", "transformer",
    "pump", "well", "treatment", "flow", "tank", "valve", "reservoir",
    "plant", "factory", "line1", "cell", "mes", "yokogawa"
}

# Sector tokens
FINANCE_TOKENS = {"banking", "payments", "corebank", "swift", "sepa", "visa"}
HEALTH_TOKENS = {"his", "ehr", "emr", "clinical", "pacs"}
TELCO_TOKENS = {"bss", "oss", "ims", "hlr", "5g", "lte"}
GOV_TOKENS = {"citizen", "justice", "tax", "financas", "registry"}
ECOMMERCE_TOKENS = {"checkout", "payment", "orders", "cart"}

# Data & Storage
DATABASE_TOKENS = {
    "db", "database", "sql", "nosql", "rds", "aurora", "postgres", "postgresql",
    "mysql", "mariadb", "mongo", "mongodb", "redis", "cassandra", "dynamo",
    "elasticsearch", "elastic", "opensearch", "neo4j", "influx", "timeseries",
    "bigquery", "snowflake", "redshift", "clickhouse", "vertica", "cockroach"
}

STORAGE_TOKENS = {
    "storage", "bucket", "s3", "blob", "objectstore", "filestore", "efs", "nfs",
    "nas", "san", "backup", "snapshots", "archive", "vault"
}

# Cloud & Infra
CLOUD_INFRA_TOKENS = {
    "iam", "kms", "secrets", "secretsmanager", "vault", "keyvault",
    "loadbalancer", "lb", "elb", "alb", "nlb", "proxy", "reverseproxy",
    "gateway", "apigateway", "firewall", "waf", "bastion", "jump", "jumphost",
    "vpn", "wireguard", "openvpn", "zerotrust", "ztna"
}

ORCHESTRATION_TOKENS = {
    "k8s", "kubernetes", "eks", "aks", "gke",
    "docker", "container", "containerd", "pod", "namespace",
    "helm", "argo", "flux", "istio", "linkerd", "mesh"
}

CI_CD_TOKENS = {
    "ci", "cd", "pipeline", "jenkins", "gitlab", "github", "actions",
    "bitbucket", "bamboo", "teamcity", "circleci", "drone"
}

# Enterprise systems
ENTERPRISE_TOKENS = {
    "sap", "oracle", "peoplesoft", "workday", "dynamics", "navision",
    "crm", "erp", "billing", "invoicing", "finance", "payments",
    "treasury", "accounting", "hr", "payroll", "identity", "sso", "oauth"
}


# --------------------------------------------------------------------------------------------------
def enrich_tags(subdomain: str, services: list) -> set:
    """
    Infer additional tags from subdomain name and services.
    """
    tags = set()

    # Subdomain-based hints
    s = subdomain.lower()
    if any(k in s for k in ["admin", "auth", "login"]): tags.add("admin")
    if any(k in s for k in ["api", "graphql"]): tags.add("api")
    if any(k in s for k in ["internal", "eng", "engineering"]): tags.add("internal")
    if any(k in s for k in ["prod", "production"]): tags.add("prod")
    elif any(k in s for k in ["stage", "staging", "preprod"]): tags.add("staging")
    elif any(k in s for k in ["dev", "test", "qa"]): tags.add("dev")
    if any(k in s for k in ["cloud", "aws", "azure", "gcp"]): tags.add("cloud")
    if any(k in s for k in ["monitor", "grafana", "kibana", "sentry", "prometheus"]): tags.add("monitoring")

    # Services-based hints
    for svc in services:
        svc = str(svc).lower()
        if svc in ["ssh", "22"]: tags.add("ssh")
        if svc in ["rdp", "3389"]: tags.add("rdp")
        if svc in ["mysql", "postgres", "3306", "5432"]: tags.add("db")
        if svc in ["http", "https", "80", "443"]: tags.add("web")
        if svc in ["modbus", "opc", "dnp3", "bacnet", "mqtt"]: tags.add("scada")

    return tags

# --------------------------------------------------------------------------------------------------
def infer_infrastructure_role(subdomain: str) -> set:
    tags = set()
    s = subdomain.lower()

    for role, cfg in INFRASTRUCTURE_PATTERNS.items():
        if any(p in s for p in cfg["patterns"]):
            tags |= cfg["tags"]
            tags.add(role)

    return tags


# --------------------------------------------------------------------------------------------------
def compute_impact_score(semantic: dict) -> dict:
    """
    Compute numeric impact score from semantic classification.
    Enriched with sector, infra, ICS/SCADA, and monitoring.
    """
    score = 0

    raw_tags = semantic.get("tags", [])
    if not isinstance(raw_tags, (list, set)):
        raw_tags = []

    tags = set(raw_tags)
    subdomain = semantic.get("subdomain", "")
    services = semantic.get("services", [])

    # Enrich tags automatically
    tags |= enrich_tags(subdomain, services)
    tags |= infer_infrastructure_role(subdomain)

    # Token inference from subdomain name
    for token_set, tag in [
        (DATABASE_TOKENS, "db"),
        (STORAGE_TOKENS, "storage"),
        (CLOUD_INFRA_TOKENS, "infra"),
        (ORCHESTRATION_TOKENS, "orchestration"),
        (CI_CD_TOKENS, "cicd"),
        (ENTERPRISE_TOKENS, "enterprise"),
    ]:
        if any(t in subdomain.lower() for t in token_set):
            tags.add(tag)

    reasons = []

    # 🔥 IT attack surfaces
    if "admin" in tags: score += 40; reasons.append("admin interface")
    if "auth" in tags: score += 30; reasons.append("authentication service")
    if "login" in tags: score += 25; reasons.append("login endpoint")
    if "api" in tags: score += 20; reasons.append("API endpoint")
    if "graphql" in tags: score += 25; reasons.append("GraphQL API")
    if "internal" in tags: score += 25; reasons.append("internal exposure")
    if "intranet" in tags: score += 20; reasons.append("intranet access")

    if score == 0 and tags:
        reasons.append("tags detected but none mapped to scoring rules")

    # Sensitive services
    if "vpn" in tags: score += 35; reasons.append("VPN gateway")
    if "ssh" in tags: score += 30; reasons.append("SSH service")
    if "rdp" in tags: score += 35; reasons.append("remote desktop service")
    if "db" in tags or "database" in tags: score += 40; reasons.append("database service")
    if "backup" in tags: score += 35; reasons.append("backup endpoint")
    if "storage" in tags or "s3" in tags or "bucket" in tags: score += 30; reasons.append("object storage")
    if "files" in tags or "download" in tags: score += 20; reasons.append("file exposure")

    # Infrastructure & orchestration
    if "k8s" in tags or "kubernetes" in tags: score += 40; reasons.append("kubernetes control plane")
    if "docker" in tags: score += 30; reasons.append("docker service")
    if "ci" in tags or "cd" in tags or "jenkins" in tags or "gitlab" in tags: score += 35; reasons.append("CI/CD infrastructure")
    if "monitoring" in tags: score += 20; reasons.append("monitoring interface")
    if "cloud" in tags: score += 15; reasons.append("cloud infrastructure")
    if "internal" in tags: score += 20; reasons.append("internal system")
    if "infra" in tags: score += 25; reasons.append("core infrastructure component")
    if "orchestration" in tags: score += 30; reasons.append("container orchestration platform")
    if "cicd" in tags: score += 30; reasons.append("CI/CD pipeline infrastructure")

    if "gateway" in tags: score += 20; reasons.append("network gateway")
    if "infra" in tags: score += 15; reasons.append("infrastructure component")
    if "edge" in tags: score += 10; reasons.append("edge service")
    if "telecom" in tags: score += 20; reasons.append("telecom service")

    # Business-critical
    if "mail" in tags or "smtp" in tags or "imap" in tags: score += 25; reasons.append("mail service")
    if "payment" in tags or "billing" in tags: score += 40; reasons.append("payment system")
    if "crm" in tags or "erp" in tags: score += 35; reasons.append("business system")

    # Environment weighting
    if "prod" in tags or "production" in tags: score += 30; reasons.append("production environment")
    elif "staging" in tags: score += 15; reasons.append("pre-production environment")
    elif "dev" in tags: score += 5; reasons.append("non-production environment")

    # Database
    if "db" in tags: score += 40; reasons.append("critical database system")
    if "storage" in tags: score += 30; reasons.append("sensitive storage system")

    # Enterprise
    if "enterprise" in tags: score += 35; reasons.append("enterprise core system")

    # Sector-based weighting
    sector = "IT"
    if tags & FINANCE_TOKENS: score += 30; reasons.append("financial sector asset"); sector="FINANCE"
    elif tags & HEALTH_TOKENS: score += 30; reasons.append("health sector asset"); sector="HEALTH"
    elif tags & TELCO_TOKENS: score += 25; reasons.append("telco core asset"); sector="TELCO"
    elif tags & GOV_TOKENS: score += 30; reasons.append("government critical service"); sector="GOV"
    elif tags & ECOMMERCE_TOKENS: score += 20; reasons.append("e-commerce transactional system"); sector="ECOMMERCE"

    # ICS / SCADA weighting
    scada_tags = tags & SCADA_TOKENS
    if scada_tags:
        ics_score = 50
        reasons.append(f"ICS/SCADA token detected: {', '.join(scada_tags)}")
        if "prod" in tags or "production" in tags: ics_score += 40; reasons.append("SCADA in production")
        elif "dev" in tags or "test" in tags: ics_score += 10; reasons.append("SCADA in non-production")
        score += ics_score

    # Infrastructure roles
    if "identity" in tags: score += 40; reasons.append("identity and access management")
    if "secrets" in tags: score += 45; reasons.append("secrets management system")
    if "database" in tags: score += 40; reasons.append("core database infrastructure")
    if "storage" in tags: score += 30; reasons.append("persistent data storage")
    if "network" in tags: score += 25; reasons.append("network control plane")
    if "orchestration" in tags: score += 35; reasons.append("container orchestration layer")
    if "cicd" in tags: score += 30; reasons.append("CI/CD infrastructure")
    if "admin" in tags: score += 40; reasons.append("administrative control interface")

    # Lower-risk / noise reduction
    if "static" in tags or "cdn" in tags: score -= 10; reasons.append("static content")
    if "assets" in tags or "images" in tags: score -= 15; reasons.append("static assets")
    if "blog" in tags or "docs" in tags: score -= 10; reasons.append("informational service")

    # Clamp score
    score = max(0, min(score, 100))

    # Priority derivation
    if score >= 90: priority = "CRITICAL"
    elif score >= 70: priority = "HIGH"
    elif score >= 40: priority = "MEDIUM"
    else: priority = "LOW"

    # Output
    semantic["impact_score"] = score
    semantic["priority"] = priority
    semantic["impact_reason"] = ", ".join(dict.fromkeys(reasons)) if reasons else "low exposure"
    if not tags:
        semantic["impact_reason"] = "no tags available for scoring"
    #semantic["tags"] = list(tags)
    semantic["tags"] = sorted(tags)
    semantic["sector"] = sector

    # ----------------------------------------------------------------------------------------------
    # 🧠 Atualização de memória estatística global
    # Guardamos os tokens inferidos e prioridade para aprendizagem futura
    try:
        update_token_stats(
            tokens=list(tags),
            severity=priority.lower(),
            domain=subdomain
        )
    except Exception:
        # Nunca deixar memória quebrar scoring principal
        pass


    #print("[DEBUG SCORE] tags before scoring:", tags)

    return semantic
