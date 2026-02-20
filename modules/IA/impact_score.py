# --------------------------------------------------------------------------------------------------
# TugaRecon - Impact Scoring (Offensive Realistic)
# modules/IA/impact_score.py
# Author: Skynet0x01 2020-2026
# --------------------------------------------------------------------------------------------------

"""
    Módulo avançado de cálculo de impacto de subdomínios e serviços.
    Funcionalidade “offensive realistic”:
    - Multiplicadores por ambiente e tipo de subdomínio
    - Pesos diferentes por categoria de tokens
    - Impact reason detalhado com contribuição de cada token
    - Usa todos os tokens disponíveis
    - Atualiza memória estatística
"""

from modules.IA.token_memory import update_token_stats
from modules.IA.heuristics import (
    SCADA_TOKENS,
    FINANCE_TOKENS,
    HEALTH_TOKENS,
    TELCO_TOKENS,
    GOV_TOKENS,
    EDU_TOKENS,
    ECOMMERCE_TOKENS,
    MANAGEMENT_TOKENS,
    API_LIKE_TOKENS,
    expand_weighted
)

# --------------------------------------------------------------------------------------------------
# Infraestrutura crítica
# Padrões de infraestrutura crítica (2026) para detecção automática
# --------------------------------------------------------------------------------------------------
INFRASTRUCTURE_PATTERNS = {
    # Gestão de identidades e autenticação
    "identity": {
        "patterns": ["auth", "sso", "iam", "login", "oauth", "oidc", "keycloak", "okta", "jumpcloud", "cognito", "azuread", "pingid"],
        "tags": {"auth", "identity", "critical"}
    },
    # Gestão de segredos e chaves
    "secrets": {
        "patterns": ["vault", "kms", "secrets", "keyvault", "keystore", "gcp-secret-manager", "aws-secretsmanager", "hashicorp", "passbolt", "1password"],
        "tags": {"secrets", "infra", "critical"}
    },
    # Bases de dados e data lakes
    "database": {
        "patterns": ["db", "database", "sql", "rds", "aurora", "postgres", "mysql", "mongo", "redis", "dynamodb", "bigquery", "snowflake", "cassandra", "timescaledb"],
        "tags": {"db", "data", "critical"}
    },
    # Armazenamento e backups
    "storage": {
        "patterns": ["s3", "bucket", "storage", "blob", "efs", "nfs", "backup", "archive", "gcs", "azureblob", "minio", "ceph", "databricks"],
        "tags": {"storage", "data"}
    },
    # Rede e edge
    "network": {
        "patterns": ["gateway", "apigateway", "proxy", "lb", "loadbalancer", "edge", "waf", "cloudflare", "fastly", "nginx", "traefik", "istio-gateway", "cilium"],
        "tags": {"network", "infra"}
    },
    # Orquestração de containers e microserviços
    "orchestration": {
        "patterns": ["k8s", "kubernetes", "eks", "aks", "gke", "cluster", "istio", "linkerd", "nomad", "docker-swarm", "openshift"],
        "tags": {"orchestration", "infra"}
    },
    # CI/CD moderno e pipelines
    "cicd": {
        "patterns": ["ci", "cd", "pipeline", "jenkins", "gitlab", "actions", "circleci", "travis", "tekton", "argo", "spinnaker", "bamboo"],
        "tags": {"cicd", "infra"}
    },
    # Observabilidade e monitoramento
    "observability": {
        "patterns": ["grafana", "prometheus", "kibana", "sentry", "monitor", "datadog", "newrelic", "splunk", "elastic", "jaeger", "opentelemetry"],
        "tags": {"monitoring", "ops"}
    },
    # Acesso administrativo crítico
    "admin": {
        "patterns": ["admin", "root", "control", "master", "console", "superuser", "sudo", "sysadmin", "portal", "dashboard", "mgmt"],
        "tags": {"admin", "critical"}
    },
    # Serviços cloud modernos e serverless
    "cloud-native": {
        "patterns": ["lambda", "functions", "fargate", "cloud-run", "app-service", "serverless", "keda", "eventbridge", "step-functions"],
        "tags": {"cloud", "serverless", "infra"}
    },
    # Zero Trust / segurança de rede moderna
    "zero-trust": {
        "patterns": ["ztna", "vpn-less", "private-endpoint", "secure-access", "identity-proxy", "perimeterless"],
        "tags": {"security", "network", "critical"}
    }
}

# --------------------------------------------------------------------------------------------------
# Enriquecer tags de subdomínio e serviços
# --------------------------------------------------------------------------------------------------
def enrich_tags(subdomain: str, services: list) -> set:
    tags = set()
    s = subdomain.lower()

    # Heurísticas de nome
    if any(k in s for k in ["admin", "auth", "login"]): tags.add("admin")
    if any(k in s for k in ["api", "graphql"]): tags.add("api")
    if any(k in s for k in ["internal", "eng", "engineering"]): tags.add("internal")
    if any(k in s for k in ["prod", "production"]): tags.add("prod")
    elif any(k in s for k in ["stage", "staging", "preprod"]): tags.add("staging")
    elif any(k in s for k in ["dev", "test", "qa"]): tags.add("dev")
    if any(k in s for k in ["cloud", "aws", "azure", "gcp"]): tags.add("cloud")

    # Heurísticas de serviços
    for svc in services:
        svc = str(svc).lower()
        if svc in ["ssh", "22"]: tags.add("ssh")
        if svc in ["rdp", "3389"]: tags.add("rdp")
        if svc in ["mysql", "postgres", "3306", "5432"]: tags.add("db")
        if svc in ["http", "https", "80", "443"]: tags.add("web")
        if svc in ["modbus", "opc", "dnp3", "bacnet", "mqtt"]: tags.add("scada")

    return tags

# --------------------------------------------------------------------------------------------------
# Inferir papel de infraestrutura crítica
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
# Multiplicadores por categoria (SCADA mais crítico)
# --------------------------------------------------------------------------------------------------
CATEGORY_MULTIPLIERS = {
    "SCADA/ICS": 2.0,
    "Finance": 1.5,
    "Health": 1.4,
    "Telco": 1.3,
    "Government": 1.3,
    "Education": 1.1,
    "E-commerce": 1.2,
    "Management/API": 1.2,
}

# Multiplicadores adicionais por tag
TAG_MULTIPLIERS = {
    "prod": 1.5,
    "admin": 1.5,
    "internal": 1.3,
    "cloud": 1.1
}

# --------------------------------------------------------------------------------------------------
# Função principal de cálculo de impacto (ofensive-realistic)
# --------------------------------------------------------------------------------------------------
def compute_impact_score(semantic: dict) -> dict:
    score = 0
    raw_tags = semantic.get("tags", [])
    if not isinstance(raw_tags, (list, set)):
        raw_tags = []
    tags = set(raw_tags)
    subdomain = semantic.get("subdomain", "")
    services = semantic.get("services", [])

    # Enriquecimento de tags
    tags |= enrich_tags(subdomain, services)
    tags |= infer_infrastructure_role(subdomain)
    reasons = []

    # Categorias de tokens
    TOKEN_CATEGORIES = {
        "SCADA/ICS": SCADA_TOKENS,
        "Finance": FINANCE_TOKENS,
        "Health": HEALTH_TOKENS,
        "Telco": TELCO_TOKENS,
        "Government": GOV_TOKENS,
        "Education": EDU_TOKENS,
        "E-commerce": ECOMMERCE_TOKENS,
        "Management/API": MANAGEMENT_TOKENS | API_LIKE_TOKENS,
    }

    # Calcular score para cada token e aplicar multiplicadores
    for category, token_set in TOKEN_CATEGORIES.items():
        matched_tokens = tags & token_set
        cat_multiplier = CATEGORY_MULTIPLIERS.get(category, 1.0)
        for token in matched_tokens:
            expansions = expand_weighted(token)
            token_score = sum(weight for _, weight in expansions) * cat_multiplier
            # aplicar multiplicadores por tag
            for t in TAG_MULTIPLIERS:
                if t in tags:
                    token_score *= TAG_MULTIPLIERS[t]
            token_score = min(100 - score, token_score)  # não ultrapassar 100
            if token_score > 0:
                score += token_score
                reasons.append(f"{category} token '{token}' -> +{token_score:.1f}")

    # Score adicional para serviços sensíveis
    if "ssh" in tags: score += min(30, 100 - score); reasons.append("SSH service")
    if "rdp" in tags: score += min(35, 100 - score); reasons.append("Remote Desktop")
    if "db" in tags: score += min(40, 100 - score); reasons.append("Critical DB")
    if "web" in tags: score += min(20, 100 - score); reasons.append("Web service")
    if "scada" in tags: score += min(50, 100 - score); reasons.append("SCADA/ICS service")

    # Garantir limite de 0-100
    score = max(0, min(score, 100))

    # Determinar prioridade
    if score >= 90: priority = "CRITICAL"
    elif score >= 70: priority = "HIGH"
    elif score >= 40: priority = "MEDIUM"
    else: priority = "LOW"

    # Atualizar dicionário semântico
    semantic["impact_score"] = score
    semantic["priority"] = priority
    semantic["impact_reason"] = ", ".join(dict.fromkeys(reasons)) if reasons else "low exposure"
    semantic["tags"] = sorted(tags)

    # Atualizar memória estatística
    try:
        update_token_stats(tokens=list(tags), severity=priority.lower(), domain=subdomain)
    except Exception:
        pass

    return semantic
#
# """
# Módulo responsável pelo cálculo do impacto de subdomínios e serviços.
# O impacto é quantificado usando heurísticas semânticas, padrões de infraestrutura,
# categorias críticas e serviços expostos.
#
# Funcionalidades:
# - Usa todos os tokens heurísticos disponíveis (SCADA, FINANCE, HEALTH, TELCO, GOV, EDU, ECOMMERCE, MANAGEMENT/API)
# - Expande tokens com pesos heurísticos usando expand_weighted
# - Acumula score com limite máximo de 100
# - Gera prioridade e justificativa textual (impact_reason)
# - Atualiza memória estatística para aprendizado de padrões de severidade
# """
#
# # --------------------------------------------------------------------------------------------------
# # Importações
# # --------------------------------------------------------------------------------------------------
# from modules.IA.token_memory import update_token_stats
# from modules.IA.heuristics import (
#     SCADA_TOKENS,
#     FINANCE_TOKENS,
#     HEALTH_TOKENS,
#     TELCO_TOKENS,
#     GOV_TOKENS,
#     EDU_TOKENS,
#     ECOMMERCE_TOKENS,
#     MANAGEMENT_TOKENS,
#     API_LIKE_TOKENS,
#     expand_weighted
# )
#
# # --------------------------------------------------------------------------------------------------
# # Padrões de infraestrutura crítica para detecção automática
# # --------------------------------------------------------------------------------------------------
# INFRASTRUCTURE_PATTERNS = {
#     "identity": {"patterns": ["auth", "sso", "iam", "login", "oauth", "oidc", "keycloak"], "tags": {"auth", "identity", "critical"}},
#     "secrets": {"patterns": ["vault", "kms", "secrets", "keyvault", "keystore"], "tags": {"secrets", "infra", "critical"}},
#     "database": {"patterns": ["db", "database", "sql", "rds", "aurora", "postgres", "mysql", "mongo", "redis"], "tags": {"db", "data", "critical"}},
#     "storage": {"patterns": ["s3", "bucket", "storage", "blob", "efs", "nfs", "backup", "archive"], "tags": {"storage", "data"}},
#     "network": {"patterns": ["gateway", "apigateway", "proxy", "lb", "loadbalancer", "edge", "waf"], "tags": {"network", "infra"}},
#     "orchestration": {"patterns": ["k8s", "kubernetes", "eks", "aks", "gke", "cluster", "istio"], "tags": {"orchestration", "infra"}},
#     "cicd": {"patterns": ["ci", "cd", "pipeline", "jenkins", "gitlab", "actions"], "tags": {"cicd", "infra"}},
#     "observability": {"patterns": ["grafana", "prometheus", "kibana", "sentry", "monitor"], "tags": {"monitoring", "ops"}},
#     "admin": {"patterns": ["admin", "root", "control", "master", "console"], "tags": {"admin", "critical"}}
# }
#
# # --------------------------------------------------------------------------------------------------
# # Função para enriquecer tags com base em subdomínio e serviços detectados
# # --------------------------------------------------------------------------------------------------
# def enrich_tags(subdomain: str, services: list) -> set:
#     """
#     Detecta heurísticas adicionais com base em padrões de nomes de subdomínio
#     e serviços detectados.
#     Retorna um conjunto de tags.
#     """
#     tags = set()
#     s = subdomain.lower()
#
#     # Heurísticas baseadas no nome do subdomínio
#     if any(k in s for k in ["admin", "auth", "login"]): tags.add("admin")
#     if any(k in s for k in ["api", "graphql"]): tags.add("api")
#     if any(k in s for k in ["internal", "eng", "engineering"]): tags.add("internal")
#     if any(k in s for k in ["prod", "production"]): tags.add("prod")
#     elif any(k in s for k in ["stage", "staging", "preprod"]): tags.add("staging")
#     elif any(k in s for k in ["dev", "test", "qa"]): tags.add("dev")
#     if any(k in s for k in ["cloud", "aws", "azure", "gcp"]): tags.add("cloud")
#
#     # Heurísticas baseadas em serviços
#     for svc in services:
#         svc = str(svc).lower()
#         if svc in ["ssh", "22"]: tags.add("ssh")
#         if svc in ["rdp", "3389"]: tags.add("rdp")
#         if svc in ["mysql", "postgres", "3306", "5432"]: tags.add("db")
#         if svc in ["http", "https", "80", "443"]: tags.add("web")
#         if svc in ["modbus", "opc", "dnp3", "bacnet", "mqtt"]: tags.add("scada")
#
#     return tags
#
# # --------------------------------------------------------------------------------------------------
# # Função para inferir papel crítico de infraestrutura
# # --------------------------------------------------------------------------------------------------
# def infer_infrastructure_role(subdomain: str) -> set:
#     """
#     Verifica padrões de subdomínio contra infraestrutura crítica.
#     Retorna tags adicionais associadas ao papel detectado.
#     """
#     tags = set()
#     s = subdomain.lower()
#     for role, cfg in INFRASTRUCTURE_PATTERNS.items():
#         if any(p in s for p in cfg["patterns"]):
#             tags |= cfg["tags"]  # Adiciona tags da infraestrutura
#             tags.add(role)        # Marca o tipo de infraestrutura
#     return tags
#
# # --------------------------------------------------------------------------------------------------
# # Função principal: calcular impacto de subdomínio
# # --------------------------------------------------------------------------------------------------
# def compute_impact_score(semantic: dict) -> dict:
#     """
#     Recebe dicionário semântico (subdomain + serviços + tags).
#     Retorna o dicionário atualizado com:
#     - impact_score (0-100)
#     - priority (LOW / MEDIUM / HIGH / CRITICAL)
#     - impact_reason (justificação textual)
#     - tags (final, ordenadas)
#     """
#     score = 0
#     raw_tags = semantic.get("tags", [])
#     if not isinstance(raw_tags, (list, set)):
#         raw_tags = []
#     tags = set(raw_tags)
#     subdomain = semantic.get("subdomain", "")
#     services = semantic.get("services", [])
#
#     # Enriquecimento de tags via heurísticas e infra
#     tags |= enrich_tags(subdomain, services)
#     tags |= infer_infrastructure_role(subdomain)
#     reasons = []
#
#     # Categorias de tokens a usar
#     TOKEN_CATEGORIES = {
#         "SCADA/ICS": SCADA_TOKENS,
#         "Finance": FINANCE_TOKENS,
#         "Health": HEALTH_TOKENS,
#         "Telco": TELCO_TOKENS,
#         "Government": GOV_TOKENS,
#         "Education": EDU_TOKENS,
#         "E-commerce": ECOMMERCE_TOKENS,
#         "Management/API": MANAGEMENT_TOKENS | API_LIKE_TOKENS,
#     }
#
#     # Para cada token detetado em cada categoria, expande e soma score
#     for category, token_set in TOKEN_CATEGORIES.items():
#         matched_tokens = tags & token_set
#         for token in matched_tokens:
#             expansions = expand_weighted(token)
#             token_score = sum(weight for _, weight in expansions)
#             token_score = min(100 - score, token_score)  # não ultrapassar 100
#             if token_score > 0:
#                 score += token_score
#                 reasons.append(f"{category} token '{token}' -> +{token_score:.1f}")
#
#     # Serviços sensíveis adicionais
#     if "ssh" in tags: score += min(30, 100 - score); reasons.append("SSH service")
#     if "rdp" in tags: score += min(35, 100 - score); reasons.append("Remote Desktop")
#     if "db" in tags: score += min(40, 100 - score); reasons.append("Critical DB")
#     if "web" in tags: score += min(20, 100 - score); reasons.append("Web service")
#
#     # Garantir score entre 0 e 100
#     score = max(0, min(score, 100))
#
#     # Determinar prioridade
#     if score >= 90: priority = "CRITICAL"
#     elif score >= 70: priority = "HIGH"
#     elif score >= 40: priority = "MEDIUM"
#     else: priority = "LOW"
#
#     # Atualizar dicionário semântico
#     semantic["impact_score"] = score
#     semantic["priority"] = priority
#     semantic["impact_reason"] = ", ".join(dict.fromkeys(reasons)) if reasons else "low exposure"
#     semantic["tags"] = sorted(tags)
#
#     # Atualizar memória estatística (aprendizado de severidade)
#     try:
#         update_token_stats(tokens=list(tags), severity=priority.lower(), domain=subdomain)
#     except Exception:
#         pass
#
#     return semantic