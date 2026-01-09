# modules/ia_subdomain/impact_score.py

"""
Impact scoring engine for TugaRecon.

Purpose:
Assign a numeric priority score to a subdomain based on
semantic classification and pentest relevance.

Score range: 0–100
Higher = higher priority
"""

# Base weights for semantic tags
TAG_WEIGHTS = {
    "admin": 40,
    "auth": 35,
    "api": 25,
    "internal": 20,
    "vpn": 25,
    "intranet": 15,
    "backend": 20,
    "frontend": 10,
}

# Environment weights
ENV_WEIGHTS = {
    "production": 30,
    "prod": 30,
    "preprod": 20,
    "staging": 15,
    "stage": 15,
    "uat": 10,
    "qa": 10,
    "test": 5,
    "dev": 2,
}

# Explicit risk hint bonus
RISK_HINT_BONUS = {
    "HIGH": 25,
    "MEDIUM": 10,
    "LOW": 0,
}

# Dangerous combinations (multipliers)
COMBO_MULTIPLIERS = [
    ({"admin", "prod"}, 1.5),
    ({"admin", "production"}, 1.5),
    ({"auth", "prod"}, 1.4),
    ({"api", "prod"}, 1.3),
]

#
# def compute_impact_score(semantic: dict) -> dict:
#     """
#     Compute a numeric impact score based on semantic classification.
#     Returns the same dict enriched with 'impact_score' and 'priority'.
#     """
#
#     score = 0
#     tags = set(semantic.get("tags", []))
#     risk_hint = semantic.get("risk_hint", "LOW")
#
#     # Base tag scoring
#     for tag in tags:
#         score += TAG_WEIGHTS.get(tag, 0)
#         score += ENV_WEIGHTS.get(tag, 0)
#
#     # Risk hint bonus
#     score += RISK_HINT_BONUS.get(risk_hint, 0)
#
#     # Apply dangerous combinations
#     for combo, multiplier in COMBO_MULTIPLIERS:
#         if combo.issubset(tags):
#             score = int(score * multiplier)
#
#     # Clamp score
#     score = max(0, min(score, 100))
#
#     # Human-friendly priority label
#     if score >= 80:
#         priority = "CRITICAL"
#     elif score >= 60:
#         priority = "HIGH"
#     elif score >= 35:
#         priority = "MEDIUM"
#     else:
#         priority = "LOW"
#
#     semantic["impact_score"] = score
#     semantic["priority"] = priority
#
#     return semantic

def compute_impact_score(semantic: dict) -> dict:
    """
    Compute a numeric impact score from semantic classification.
    Score is explainable, deterministic and pentester-oriented.
    """

    score = 0
    tags = set(semantic.get("tags", []))
    reasons = []

    # High-value surfaces
    if "admin" in tags:
        score += 40
        reasons.append("admin interface")

    if "auth" in tags:
        score += 30
        reasons.append("authentication service")

    if "api" in tags:
        score += 20
        reasons.append("API endpoint")

    if "internal" in tags:
        score += 25
        reasons.append("internal exposure")

    # Environment weighting
    if "prod" in tags or "production" in tags:
        score += 30
        reasons.append("production environment")
    elif "staging" in tags or "stage" in tags or "preprod" in tags:
        score += 15
        reasons.append("pre-production environment")
    elif "dev" in tags or "test" in tags or "qa" in tags:
        score += 5
        reasons.append("non-production environment")

    # Clamp score
    score = min(score, 100)

    # Priority derivation
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
    semantic["impact_reason"] = ", ".join(reasons) if reasons else "low exposure"

    return semantic
