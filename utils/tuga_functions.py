# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
import datetime
from utils.tuga_colors import G, Y, R, W

# ----------------------------------------------------------------------------------------------------------
def print_semantic_results_grouped(results):
    critical = []
    high = []
    medium = []
    low = []

    for r in results:
        # -------------------------------
        # PRIORITY — single source of truth
        priority = (
            r.get("_priority")
            or r.get("priority")
            or r.get("semantic_priority")
            or r.get("priority_label")
            or r.get("final_priority")
            or "LOW"
        )

        priority = str(priority).upper().strip()
        r["_priority"] = priority

        # -------------------------------
        # IMPACT — single source of truth
        impact = (
            r.get("_impact")
            or r.get("impact")
            or r.get("semantic_impact")
            or r.get("impact_score")
            or 0
        )

        try:
            impact = int(impact)
        except Exception:
            impact = 0

        r["_impact"] = impact

        # -------------------------------
        if priority == "CRITICAL":
            critical.append(r)
        elif priority == "HIGH":
            high.append(r)
        elif priority == "MEDIUM":
            medium.append(r)
        else:
            low.append(r)

    print("\n" + "─" * 60)
    print("[🧠] Semantic & Impact Classification")
    print("─" * 60)

    # -------------------------------------------------
    if critical:
        print("\n[ CRITICAL PRIORITY ]")
        print("-" * 80)
        print(" #   PRIORITY    IMPACT   SUBDOMAIN")
        print("-" * 80)

        for i, r in enumerate(critical, 1):
            tags = ", ".join(r.get("tags", [])) or "-"
            sub = r.get("subdomain", "unknown")

            print(
                f"{i:3}   {r['_priority']:<10} {r['_impact']:>6}   "
                f"{sub:<45} [{tags}]"
            )

    # -------------------------------------------------
    if high or medium:
        print("\n[ HIGH | MEDIUM PRIORITY ]")
        print("-" * 80)
        print(" #   PRIORITY    IMPACT   SUBDOMAIN")
        print("-" * 80)

        idx = 1
        for r in high + medium:
            tags = ", ".join(r.get("tags", [])) or "-"
            sub = r.get("subdomain", "unknown")

            print(
                f"{idx:3}   {r['_priority']:<10} {r['_impact']:>6}   "
                f"{sub:<45} [{tags}]"
            )
            idx += 1

    # -------------------------------------------------
    if low:
        print("\n" + "─" * 60)
        print("[ LOW PRIORITY ]")
        print("-" * 80)

        offset = len(critical) + len(high) + len(medium)
        for i, r in enumerate(low, offset + 1):
            sub = r.get("subdomain", "unknown")

            print(
                f"{i:3}   {r['_priority']:<10} {r['_impact']:>6}   "
                f"{sub}"
            )