# --------------------------------------------------------------------------------------------------
# TugaRecon - Contextual Impact Engine
# File: utils/context_engine.py
# Purpose: Adjust impact score based on operational context
# --------------------------------------------------------------------------------------------------

def apply_context_adjustment(entry: dict) -> dict:
    """
    Adjust impact score based on environment, exposure and role.
    This runs AFTER compute_impact_score().
    """

    score = entry.get("impact_score", 0)
    tags = set(entry.get("tags", []))
    reasons = []

    # -------------------------
    # Environment weighting
    # -------------------------
    if "prod" in tags or "production" in tags:
        score += 10
        reasons.append("production environment")
    elif "staging" in tags:
        score += 5
        reasons.append("staging environment")
    elif "dev" in tags:
        score -= 5
        reasons.append("non-production environment")

    # -------------------------
    # Exposure & trust boundary
    # -------------------------
    if "internal" in tags and "vpn" not in tags:
        score += 5
        reasons.append("internal system with trust boundary")
    if "vpn" in tags:
        score += 10
        reasons.append("remote access boundary")
    if "auth" in tags:
        score += 10
        reasons.append("authentication choke point")

    # -------------------------
    # Business critical signals
    # -------------------------
    if "billing" in tags or "payment" in tags:
        score += 15
        reasons.append("business critical service")
    if "admin" in tags:
        score += 15
        reasons.append("administrative control plane")

    # -------------------------
    # Clamp score safely
    # -------------------------
    score = max(0, min(score, 100))

    # -------------------------
    # Update entry
    # -------------------------
    entry["impact_score"] = score

    if reasons:
        previous = entry.get("impact_reason", "")
        entry["impact_reason"] = (
            previous + " | contextual: " + ", ".join(reasons)
            if previous else ", ".join(reasons)
        )

    # Recalculate priority (authoritative)
    if score >= 90:
        entry["priority"] = "CRITICAL"
    elif score >= 70:
        entry["priority"] = "HIGH"
    elif score >= 40:
        entry["priority"] = "MEDIUM"
    else:
        entry["priority"] = "LOW"

    return entry
