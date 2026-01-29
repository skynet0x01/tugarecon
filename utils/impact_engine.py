# --------------------------------------------------------------------------------------------------
# TugaRecon
# File: utils/impact_engine.py
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------
# TugaRecon - Impact Engine (Attack Surface Booster)
# Author: Skynet0x01 2020-2026
# --------------------------------------------------------------------------------------------------

CRITICAL_KEYWORDS = {
    "vpn": 30,
    "auth": 25,
    "sso": 25,
    "login": 20,
    "billing": 30,
    "payment": 30,
    "admin": 35,
    "internal": 20,
    "intranet": 20,
    "gateway": 20,
    "bastion": 30,
    "jump": 30,
}

INFRA_TAG_BOOST = {
    "identity": 25,
    "secrets": 30,
    "database": 30,
    "storage": 20,
    "network": 20,
    "orchestration": 25,
    "cicd": 20,
}

ENVIRONMENT_BOOST = {
    "prod": 25,
    "production": 25,
    "staging": 10,
    "dev": 0,
}

PRIORITY_OVERRIDE = [
    ("vpn", "HIGH"),
    ("auth", "HIGH"),
    ("billing", "HIGH"),
    ("payment", "HIGH"),
    ("admin", "CRITICAL"),
]


def apply_impact_engine(semantic: dict) -> dict:
    """
    Final attack-surface aware impact adjustment.
    Assumes semantic classification and base impact_score already exist.
    """

    score = semantic.get("impact_score", 0)
    tags = set(semantic.get("tags", []))
    subdomain = semantic.get("subdomain", "").lower()

    reasons = []

    # Keyword-based boosting (subdomain name)
    for key, boost in CRITICAL_KEYWORDS.items():
        if key in subdomain:
            score += boost
            reasons.append(f"keyword '{key}' increases attack surface")

    # Tag-based infrastructure boosting
    for tag, boost in INFRA_TAG_BOOST.items():
        if tag in tags:
            score += boost
            reasons.append(f"infrastructure role '{tag}'")

    # Environment awareness
    for env, boost in ENVIRONMENT_BOOST.items():
        if env in tags:
            score += boost
            reasons.append(f"{env} environment")

    # Priority override logic (hard attacker rules)
    for token, forced_priority in PRIORITY_OVERRIDE:
        if token in tags or token in subdomain:
            semantic["priority"] = forced_priority
            reasons.append(f"forced priority due to '{token}'")

    # Clamp again
    score = max(0, min(score, 100))
    semantic["impact_score"] = score

    # Re-derive priority if not forced
    if "priority" not in semantic or semantic["priority"] == "LOW":
        if score >= 90:
            semantic["priority"] = "CRITICAL"
        elif score >= 70:
            semantic["priority"] = "HIGH"
        elif score >= 40:
            semantic["priority"] = "MEDIUM"
        else:
            semantic["priority"] = "LOW"

    # Merge reasons
    prev_reason = semantic.get("impact_reason", "")
    merged = []
    if prev_reason:
        merged.append(prev_reason)
    merged.extend(reasons)

    semantic["impact_reason"] = ", ".join(dict.fromkeys(merged))

    return semantic
