# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
from utils.tuga_colors import G, Y, R, W

PRIORITY_ORDER = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4
}

DISPLAY_PRIORITIES = ["CRITICAL", "HIGH", "MEDIUM"]


# ----------------------------------------------------------------------------------------------------------
def normalize_priority(p):
    return (p or "LOW").upper()

def sort_by_priority_then_impact(items):
    return sorted(
        items,
        key=lambda r: (
            -PRIORITY_ORDER.get(normalize_priority(r.get("priority")), 0),
            -r.get("impact_score", r.get("impact", 0))
        )
    )

# ----------------------------------------------------------------------------------------------------------
def is_relevant_priority(priority: str) -> bool:
    if not priority:
        return False
    return PRIORITY_ORDER.get(priority.upper(), 0) >= PRIORITY_ORDER["MEDIUM"]

# ----------------------------------------------------------------------------------------------------------
def print_scan_diff(diff: dict):
    if not diff:
        print("[Δ] No differences detected.\n")
        return

    MIN_PRIORITY = PRIORITY_ORDER["MEDIUM"]

    # ----------------------------------------------------------------------------------------------------------
    def is_visible(r):
        return PRIORITY_ORDER.get(r.get("priority", "LOW"), 1) >= MIN_PRIORITY

    new = [r for r in diff.get("new", []) if is_visible(r)]
    updated = [r for r in diff.get("updated", []) if is_visible(r)]
    removed = diff.get("removed", [])  # sempre mostrar removidos

    summary = {p: 0 for p in DISPLAY_PRIORITIES}

    for section in ("new", "updated"):
        for r in diff.get(section, []):
            p = normalize_priority(r.get("priority"))
            if p in summary:
                summary[p] += 1

    if any(summary.values()):
        print("────────────────────────────────────────────────────────────")
        print("[Δ] Scan difference summary")
        print("────────────────────────────────────────────────────────────")
        print(" " + " | ".join(f"{p}: {summary[p]}" for p in DISPLAY_PRIORITIES))
        print("────────────────────────────────────────────────────────────\n")

    if not new and not updated and not removed:
        print(Y + "[✓] No relevant changes (MEDIUM+)\n" + W)
        return

    # REMOVED
    if removed:
        print(R + "\n[!] Removed since last scan" + W)
        print("-" * 70)
        for r in removed:
            priority = normalize_priority(r.get("priority", "LOW"))
            print(f" • {r['subdomain']} [{priority}]")

    # NEW + UPDATED combinados
    combined = []
    for r in new:
        r["_change"] = "NEW"
        combined.append(r)
    for r in updated:
        r["_change"] = "UPDATED"
        combined.append(r)

    combined = sort_by_priority_then_impact(combined)

    current_priority = None
    for r in combined:
        priority = normalize_priority(r.get("priority"))
        if priority not in DISPLAY_PRIORITIES:
            continue

        if priority != current_priority:
            print(f"\n[ {priority} ]")
            print("--------------------------------------------------------------------------------")
            current_priority = priority

        impact = r.get("impact_score", r.get("impact", 0))
        tags = ",".join(r.get("tags", [])) or "-"
        change = r.get("_change", "")

        color = R if priority == "CRITICAL" else Y if priority == "HIGH" else G

        print(f" {color}•{W} {r['subdomain']:<38} impact={impact:<3} tags={tags} [{change}]")

