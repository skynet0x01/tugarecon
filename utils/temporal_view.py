# --------------------------------------------------------------------------------------------------
# TugaRecon - Improved Terminal Temporal View
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# Module: utils/temporal_view.py
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
from utils.tuga_colors import G, Y, R, B, W

def print_top_temporal(temporal_rank, removed_list=None, limit=20, subdomain_width=100):
    """
    Exibe os subdomínios com maior score temporal de forma visual.
    NEW, ESCALATED, FLAPPING destacados; LOW / DORMANT e REMOVED listados separadamente.
    """

    counts = {
        "NEW": 0,
        "ESCALATED": 0,
        "FLAPPING": 0,
        "LOW_DORMANT": 0,
        "REMOVED": len(removed_list) if removed_list else 0
    }

    for e in temporal_rank:
        state = e.get("state", "")
        if state in counts:
            counts[state] += 1
        elif state in ("STABLE", "DORMANT", "LOW"):
            counts["LOW_DORMANT"] += 1

    # ───────── Header ─────────
    print("\n" + "─"*subdomain_width)
    print("[🧠] Legend: Temporal Risk View – Top Targets")
    print("─"*subdomain_width)
    print(f"Legend: {R}ESCALATED{W} | {Y}NEW{W} | {G}FLAPPING{W} | {B}DORMANT / LOW{W}")
    print(f"Counts: NEW={counts['NEW']} | ESCALATED={counts['ESCALATED']} | FLAPPING={counts['FLAPPING']} | LOW/DORMANT={counts['LOW_DORMANT']} | REMOVED={counts['REMOVED']}")
    print("-"*subdomain_width)
    print(f"{'#':<4} {'STATE':<10} SUBDOMAIN{' '*(subdomain_width-30)} SCORE  IMPACT ACTION")
    print("-"*subdomain_width)

    displayed = 0
    for entry in temporal_rank:
        if displayed >= limit:
            break
        state = entry.get("state", "")
        score = entry.get("score", 0)
        impact = entry.get("impact_score", 0)
        sub = entry.get("subdomain", "")
        action = entry.get("action", "")

        color = R if state == "ESCALATED" else Y if state == "NEW" else G if state == "FLAPPING" else W
        impact_icon = "🔥" if impact >= 50 else "⚠️" if impact >= 20 else "✅"

        if state in ("NEW", "ESCALATED", "FLAPPING"):
            displayed += 1
            print(f"{color}{displayed:<4} {state:<10} {sub:<{subdomain_width}} {score:<6} {impact_icon} {impact:<4} {action:<10}{W}")

    if displayed == 0:
        print(Y + "✓ No actionable temporal risk detected in top targets" + W)

    # LOW / DORMANT
    low_dormant = [e for e in temporal_rank if e.get("state") in ("STABLE", "DORMANT", "LOW")]
    if low_dormant:
        print("\n" + "─"*subdomain_width)
        print(f"[🧠] Temporal Change Log – LOW / DORMANT ({counts['LOW_DORMANT']})")
        print("─"*subdomain_width)
        for e in low_dormant:
            state_color = B if e["state"] == "DORMANT" else W
            sub = e.get("subdomain", "")
            score = e.get("score", 0)
            impact = e.get("impact_score", 0)
            impact_icon = "🔥" if impact >= 50 else "⚠️" if impact >= 20 else "✅"
            print(f" • {state_color}{sub:<{subdomain_width}} [{e['state']}] {impact_icon} score={score:<4} impact={impact:<4}{W}")

    # REMOVED
    if removed_list:
        print("\n" + "─"*subdomain_width)
        print(f"[🧠] Temporal Change Log – REMOVED ({counts['REMOVED']})")
        print("─"*subdomain_width)
        print("REMOVED (last seen ≥ 2 days):")
        for sub in removed_list:
            print(f" • {sub}")

#
# from utils.tuga_colors import G, Y, R, B, W
#
# def print_top_temporal(temporal_rank, removed_list=None, limit=20):
#     """
#     Exibe os subdomínios com maior score temporal de forma visual.
#     NEW, ESCALATED, FLAPPING destacados; LOW / DORMANT e REMOVED listados separadamente.
#     """
#
#     # ───────── Contadores ─────────
#     counts = {
#         "NEW": 0,
#         "ESCALATED": 0,
#         "FLAPPING": 0,
#         "LOW_DORMANT": 0,
#         "REMOVED": len(removed_list) if removed_list else 0
#     }
#
#     for e in temporal_rank:
#         if e["state"] in ("NEW", "ESCALATED", "FLAPPING"):
#             counts[e["state"]] += 1
#         elif e["state"] in ("STABLE", "DORMANT", "LOW"):
#             counts["LOW_DORMANT"] += 1
#
#     # ───────── Header + Legenda ─────────
#     print("\n──────────────────────────────────────────────────────────────────────")
#     print("[🧠] Legend: Temporal Risk View – Top Targets")
#     print("──────────────────────────────────────────────────────────────────────")
#     print(f"Legend: {R}ESCALATED{W} | {Y}NEW{W} | {G}FLAPPING{W} | {B}DORMANT / LOW{W}")
#     print(f"Counts: NEW={counts['NEW']} | ESCALATED={counts['ESCALATED']} | FLAPPING={counts['FLAPPING']} | LOW/DORMANT={counts['LOW_DORMANT']} | REMOVED={counts['REMOVED']}")
#     print("-" * 70)
#     print(f"{'#':<4} {'STATE':<10} {'SCORE':<6} {'IMPACT':<6} {'ACTION':<10} SUBDOMAIN")
#     print("-" * 70)
#
#     # ───────── Tabela principal (Riscos acionáveis) ─────────
#     displayed = 0
#     for entry in temporal_rank:
#         if displayed >= limit:
#             break
#
#         state = entry.get("state", "")
#         score = entry.get("score", 0)
#         #impact = entry.get("impact", 0)
#         impact = entry.get("impact_score", 0)
#         sub = entry.get("subdomain", "")
#         action = entry.get("action", "")
#
#         color = R if state == "ESCALATED" else Y if state == "NEW" else G if state == "FLAPPING" else W
#
#         if state in ("NEW", "ESCALATED", "FLAPPING"):
#             displayed += 1
#             print(f"{color}{displayed:<4} {state:<10} {score:<6} {impact:<6} {action:<10} {sub}{W}")
#
#     if displayed == 0:
#         print(Y + "✓ No actionable temporal risk detected in top targets" + W)
#
#     # ───────── LOW / DORMANT ─────────
#     low_dormant = [e for e in temporal_rank if e["state"] in ("STABLE", "DORMANT", "LOW")]
#     if low_dormant:
#         print("\n──────────────────────────────────────────────────────────────────────")
#         print(f"[🧠] Temporal Change Log – LOW / DORMANT ({counts['LOW_DORMANT']})")
#         print("──────────────────────────────────────────────────────────────────────")
#         for e in low_dormant:
#             state_color = B if e["state"] == "DORMANT" else W
#             print(f" • {state_color}{e['subdomain']:<40} [{e['state']}] score={e['score']} impact={e['impact']}{W}")
#
#     # ───────── REMOVED ─────────
#     if removed_list:
#         print("\n──────────────────────────────────────────────────────────────────────")
#         print(f"[🧠] Temporal Change Log – REMOVED ({counts['REMOVED']})")
#         print("──────────────────────────────────────────────────────────────────────")
#         print("REMOVED (last seen ≥ 2 days):")
#         for sub in removed_list:
#             print(f" • {sub}")
