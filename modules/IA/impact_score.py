# --------------------------------------------------------------------------------------------------
# TugaRecon - Impact Scoring (Enhanced)
# Este módulo calcula o impacto de um subdomínio com base em:
# - Tokens semânticos
# - Infraestrutura
# - Setor
# - SCADA / ICS
# - Ambiente (prod/dev)
# - Serviços expostos
# O objetivo é transformar contexto técnico em score ofensivo quantificado.
# --------------------------------------------------------------------------------------------------

from modules.IA.token_memory import update_token_stats
# Sistema de "memória" estatística que aprende padrões de severidade ao longo do tempo.


# --------------------------------------------------------------------------------------------------
# Padrões de infraestrutura críticos.
# Cada role contém:
# - padrões (strings que podem aparecer no subdomínio)
# - tags que devem ser automaticamente adicionadas
INFRASTRUCTURE_PATTERNS = {

    # Identity & Secrets (alto risco estrutural)
    "identity": {
        "patterns": ["auth", "sso", "iam", "login", "oauth", "oidc", "keycloak"],
        "tags": {"auth", "identity", "critical"}
    },

    "secrets": {
        "patterns": ["vault", "kms", "secrets", "keyvault", "keystore"],
        "tags": {"secrets", "infra", "critical"}
    },

    # Databases
    "database": {
        "patterns": ["db", "database", "sql", "rds", "aurora", "postgres", "mysql", "mongo", "redis"],
        "tags": {"db", "data", "critical"}
    },

    # Storage
    "storage": {
        "patterns": ["s3", "bucket", "storage", "blob", "efs", "nfs", "backup", "archive"],
        "tags": {"storage", "data"}
    },

    # Network
    "network": {
        "patterns": ["gateway", "apigateway", "proxy", "lb", "loadbalancer", "edge", "waf"],
        "tags": {"network", "infra"}
    },

    # Containers
    "orchestration": {
        "patterns": ["k8s", "kubernetes", "eks", "aks", "gke", "cluster", "istio"],
        "tags": {"orchestration", "infra"}
    },

    # CI/CD
    "cicd": {
        "patterns": ["ci", "cd", "pipeline", "jenkins", "gitlab", "actions"],
        "tags": {"cicd", "infra"}
    },

    # Observabilidade
    "observability": {
        "patterns": ["grafana", "prometheus", "kibana", "sentry", "monitor"],
        "tags": {"monitoring", "ops"}
    },

    # Admin
    "admin": {
        "patterns": ["admin", "root", "control", "master", "console"],
        "tags": {"admin", "critical"}
    }
}


# --------------------------------------------------------------------------------------------------
# Tokens SCADA / ICS (Industrial Control Systems)
# Estes tokens representam ambientes industriais.
# Quando detectados, o scoring sobe brutalmente.
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


# --------------------------------------------------------------------------------------------------
# Conjuntos de tokens por setor (vertical de negócio)
FINANCE_TOKENS = {"banking", "payments", "corebank", "swift", "sepa", "visa"}
HEALTH_TOKENS = {"his", "ehr", "emr", "clinical", "pacs"}
TELCO_TOKENS = {"bss", "oss", "ims", "hlr", "5g", "lte"}
GOV_TOKENS = {"citizen", "justice", "tax", "financas", "registry"}
ECOMMERCE_TOKENS = {"checkout", "payment", "orders", "cart"}


# --------------------------------------------------------------------------------------------------
def enrich_tags(subdomain: str, services: list) -> set:
    """
    Inferência automática de tags a partir:
    - Nome do subdomínio
    - Serviços detectados (portas/protocolos)
    """

    tags = set()
    s = subdomain.lower()

    # Heurísticas baseadas no nome
    if any(k in s for k in ["admin", "auth", "login"]):
        tags.add("admin")

    if any(k in s for k in ["api", "graphql"]):
        tags.add("api")

    if any(k in s for k in ["internal", "eng", "engineering"]):
        tags.add("internal")

    if any(k in s for k in ["prod", "production"]):
        tags.add("prod")
    elif any(k in s for k in ["stage", "staging", "preprod"]):
        tags.add("staging")
    elif any(k in s for k in ["dev", "test", "qa"]):
        tags.add("dev")

    if any(k in s for k in ["cloud", "aws", "azure", "gcp"]):
        tags.add("cloud")

    # Heurísticas baseadas em serviços expostos
    for svc in services:
        svc = str(svc).lower()

        if svc in ["ssh", "22"]:
            tags.add("ssh")

        if svc in ["rdp", "3389"]:
            tags.add("rdp")

        if svc in ["mysql", "postgres", "3306", "5432"]:
            tags.add("db")

        if svc in ["http", "https", "80", "443"]:
            tags.add("web")

        if svc in ["modbus", "opc", "dnp3", "bacnet", "mqtt"]:
            tags.add("scada")

    return tags


# --------------------------------------------------------------------------------------------------
def infer_infrastructure_role(subdomain: str) -> set:
    """
    Analisa o nome do subdomínio e adiciona tags estruturais
    com base nos padrões definidos em INFRASTRUCTURE_PATTERNS.
    """
    tags = set()
    s = subdomain.lower()

    for role, cfg in INFRASTRUCTURE_PATTERNS.items():
        if any(p in s for p in cfg["patterns"]):
            tags |= cfg["tags"]   # adiciona conjunto de tags
            tags.add(role)        # adiciona role principal

    return tags


# --------------------------------------------------------------------------------------------------
def compute_impact_score(semantic: dict) -> dict:
    """
    Calcula score de impacto (0–100).
    O score resulta de múltiplos fatores:
    - superfície de ataque
    - criticidade técnica
    - setor
    - ambiente
    - ICS/SCADA
    """

    score = 0

    raw_tags = semantic.get("tags", [])
    if not isinstance(raw_tags, (list, set)):
        raw_tags = []

    tags = set(raw_tags)
    subdomain = semantic.get("subdomain", "")
    services = semantic.get("services", [])

    # Enriquecimento automático
    tags |= enrich_tags(subdomain, services)
    tags |= infer_infrastructure_role(subdomain)

    reasons = []

    # ----------------------------------------------------------------------------------------------
    # Superfícies IT clássicas
    if "admin" in tags:
        score += 40
        reasons.append("admin interface")

    if "auth" in tags:
        score += 30
        reasons.append("authentication service")

    if "api" in tags:
        score += 20
        reasons.append("API endpoint")

    # ----------------------------------------------------------------------------------------------
    # Serviços sensíveis
    if "ssh" in tags:
        score += 30
        reasons.append("SSH service")

    if "rdp" in tags:
        score += 35
        reasons.append("remote desktop service")

    if "db" in tags:
        score += 40
        reasons.append("critical database system")

    # ----------------------------------------------------------------------------------------------
    # Ambiente
    if "prod" in tags:
        score += 30
        reasons.append("production environment")
    elif "staging" in tags:
        score += 15
        reasons.append("pre-production environment")
    elif "dev" in tags:
        score += 5
        reasons.append("non-production environment")

    # ----------------------------------------------------------------------------------------------
    # SCADA / ICS
    scada_tags = tags & SCADA_TOKENS
    if scada_tags:
        ics_score = 50
        reasons.append(f"ICS/SCADA token detected: {', '.join(scada_tags)}")

        if "prod" in tags:
            ics_score += 40
            reasons.append("SCADA in production")

        score += ics_score

    # ----------------------------------------------------------------------------------------------
    # Limita score entre 0 e 100
    score = max(0, min(score, 100))

    # Derivação de prioridade
    if score >= 90:
        priority = "CRITICAL"
    elif score >= 70:
        priority = "HIGH"
    elif score >= 40:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    # Atualiza estrutura semantic
    semantic["impact_score"] = score
    semantic["priority"] = priority
    semantic["impact_reason"] = ", ".join(dict.fromkeys(reasons)) if reasons else "low exposure"
    semantic["tags"] = sorted(tags)

    # ----------------------------------------------------------------------------------------------
    # Atualiza memória estatística (aprendizagem passiva)
    try:
        update_token_stats(
            tokens=list(tags),
            severity=priority.lower(),
            domain=subdomain
        )
    except Exception:
        # Nunca comprometer scoring principal
        pass

    return semantic
