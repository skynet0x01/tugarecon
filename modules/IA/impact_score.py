# --------------------------------------------------------------------------------------------------
# TugaRecon - Impact Scoring (Enhanced)
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

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
def compute_impact_score(semantic: dict) -> dict:
    """
    Compute numeric impact score from semantic classification.
    Enriched with sector, infra, ICS/SCADA, and monitoring.
    """
    score = 0
    tags = set(semantic.get("tags", []))
    subdomain = semantic.get("subdomain", "")
    services = semantic.get("services", [])

    # Enrich tags automatically
    tags |= enrich_tags(subdomain, services)

    reasons = []

    # 🔥 IT attack surfaces
    if "admin" in tags: score += 40; reasons.append("admin interface")
    if "auth" in tags: score += 30; reasons.append("authentication service")
    if "login" in tags: score += 25; reasons.append("login endpoint")
    if "api" in tags: score += 20; reasons.append("API endpoint")
    if "graphql" in tags: score += 25; reasons.append("GraphQL API")
    if "internal" in tags: score += 25; reasons.append("internal exposure")
    if "intranet" in tags: score += 20; reasons.append("intranet access")

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

    # Business-critical
    if "mail" in tags or "smtp" in tags or "imap" in tags: score += 25; reasons.append("mail service")
    if "payment" in tags or "billing" in tags: score += 40; reasons.append("payment system")
    if "crm" in tags or "erp" in tags: score += 35; reasons.append("business system")

    # Environment weighting
    if "prod" in tags or "production" in tags: score += 30; reasons.append("production environment")
    elif "staging" in tags: score += 15; reasons.append("pre-production environment")
    elif "dev" in tags: score += 5; reasons.append("non-production environment")

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

    # Lower-risk / noise reduction
    if "static" in tags or "cdn" in tags: score -= 10; reasons.append("static content")
    if "assets" in tags or "images" in tags: score -= 15; reasons.append("static assets")

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
    semantic["tags"] = list(tags)
    semantic["sector"] = sector

    return semantic
