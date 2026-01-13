from utils.tuga_colors import G, Y, R, W

STATE_ICON = {
    "NEW": "🆕",
    "ESCALATED": "⬆️",
    "FLAPPING": "🔁",
    "STABLE": "•",
    "DORMANT": "💤"
}

def print_top_temporal(subdomains, limit=20):
    """
    Mostra apenas os subdomínios mais relevantes
    esperados no formato:
    {
      subdomain, temporal_score, impact, priority, tags, state
    }
    """

    print("\n" + "─" * 70)
    print("[🧠] Temporal Risk View – Top Targets")
    print("─" * 70)

    header = f"{'#':<3} {'S':<2} {'SCORE':<6} {'IMPACT':<6} {'PRIO':<8} SUBDOMAIN"
    print(header)
    print("-" * len(header))

    for i, r in enumerate(subdomains[:limit], 1):
        score = r.get("temporal_score", 0)
        impact = r.get("impact", 0)
        prio = r.get("priority", "LOW")
        state = r.get("state", "STABLE")
        tags = ",".join(r.get("tags", [])) or "-"

        icon = STATE_ICON.get(state, "•")

        if prio == "CRITICAL":
            color = R
        elif prio == "HIGH":
            color = Y
        else:
            color = G

        print(
            f"{i:<3} {icon:<2} {score:<6} {impact:<6} "
            f"{color}{prio:<8}{W} {r['subdomain']} [{tags}]"
        )

    print("─" * 70)
