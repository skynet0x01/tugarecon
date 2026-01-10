
def compute_impact_score(semantic: dict) -> dict:
    """
    Compute a numeric impact score from semantic classification.
    Score is explainable, deterministic and pentester-oriented.
    """

    score = 0
    tags = set(semantic.get("tags", []))
    reasons = []

    # ------------------------------------------------------------------
    # 🔥 High-value attack surfaces
    # ------------------------------------------------------------------
    if "admin" in tags:
        score += 40
        reasons.append("admin interface")

    if "auth" in tags:
        score += 30
        reasons.append("authentication service")

    if "login" in tags:
        score += 25
        reasons.append("login endpoint")

    if "api" in tags:
        score += 20
        reasons.append("API endpoint")

    if "graphql" in tags:
        score += 25
        reasons.append("GraphQL API")

    if "internal" in tags:
        score += 25
        reasons.append("internal exposure")

    if "intranet" in tags:
        score += 20
        reasons.append("intranet access")

    # ------------------------------------------------------------------
    # 🔐 Sensitive services / data
    # ------------------------------------------------------------------
    if "vpn" in tags:
        score += 35
        reasons.append("VPN gateway")

    if "ssh" in tags:
        score += 30
        reasons.append("SSH service")

    if "rdp" in tags:
        score += 35
        reasons.append("remote desktop service")

    if "db" in tags or "database" in tags:
        score += 40
        reasons.append("database service")

    if "backup" in tags:
        score += 35
        reasons.append("backup endpoint")

    if "storage" in tags or "s3" in tags or "bucket" in tags:
        score += 30
        reasons.append("object storage")

    if "files" in tags or "download" in tags:
        score += 20
        reasons.append("file exposure")

    # ------------------------------------------------------------------
    # ☁️ Infrastructure & orchestration
    # ------------------------------------------------------------------
    if "k8s" in tags or "kubernetes" in tags:
        score += 40
        reasons.append("kubernetes control plane")

    if "docker" in tags:
        score += 30
        reasons.append("docker service")

    if "ci" in tags or "cd" in tags or "jenkins" in tags or "gitlab" in tags:
        score += 35
        reasons.append("CI/CD infrastructure")

    if "monitoring" in tags or "metrics" in tags or "prometheus" in tags:
        score += 20
        reasons.append("monitoring interface")

    # ------------------------------------------------------------------
    # 📧 Business-critical services
    # ------------------------------------------------------------------
    if "mail" in tags or "smtp" in tags or "imap" in tags:
        score += 25
        reasons.append("mail service")

    if "payment" in tags or "billing" in tags:
        score += 40
        reasons.append("payment system")

    if "crm" in tags or "erp" in tags:
        score += 35
        reasons.append("business system")

    # ------------------------------------------------------------------
    # 🌍 Environment weighting
    # ------------------------------------------------------------------
    if "prod" in tags or "production" in tags:
        score += 30
        reasons.append("production environment")

    elif "staging" in tags or "stage" in tags or "preprod" in tags:
        score += 15
        reasons.append("pre-production environment")

    elif "dev" in tags or "test" in tags or "qa" in tags:
        score += 5
        reasons.append("non-production environment")

    # ------------------------------------------------------------------
    # 🧪 Lower-risk / noise reduction
    # ------------------------------------------------------------------
    if "static" in tags or "cdn" in tags:
        score -= 10
        reasons.append("static content")

    if "assets" in tags or "images" in tags:
        score -= 15
        reasons.append("static assets")

    # ------------------------------------------------------------------
    # Clamp score
    # ------------------------------------------------------------------
    score = max(0, min(score, 100))

    # ------------------------------------------------------------------
    # Priority derivation
    # ------------------------------------------------------------------
    if score >= 90:
        priority = "CRITICAL"
    elif score >= 70:
        priority = "HIGH"
    elif score >= 40:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    semantic["impact_score"] = score
    semantic["priority"] = priority
    semantic["impact_reason"] = ", ".join(dict.fromkeys(reasons)) if reasons else "low exposure"

    return semantic

