def derive_attack_state(entry):
    """
    Derives attacker-relevant properties from an entry.
    No scanning. No guessing. Pure inference.
    """

    tags = set(t.lower() for t in entry.get("tags", []))
    impact = entry.get("impact_score", 0)
    priority = entry.get("_priority", "LOW")
    exposure = entry.get("exposure", "unknown")
    environment = entry.get("environment", "unknown")

    entry_point = any(t in tags for t in {
        "web", "api", "vpn", "auth", "mail", "exposed"
    })

    pivotable = any(t in tags for t in {
        "internal", "infra", "orchestration", "ci", "admin"
    })

    crown_jewel = priority == "CRITICAL" or impact >= 90

    # Cost: quanto menor, mais atrativo
    cost = 100 - impact

    if exposure == "external":
        cost -= 10
    if environment in ("prod", "production"):
        cost += 5
    if "vpn" in tags or "auth" in tags:
        cost -= 10

    entry["attack_surface"] = {
        "entry_point": entry_point,
        "pivotable": pivotable,
        "crown_jewel": crown_jewel,
        "cost": max(cost, 1)
    }

    return entry
