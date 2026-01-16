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

def analyze_temporal_state(current_snapshot, previous_snapshot):
    """
    Compara dois snapshots e devolve estados temporais por subdomínio
    """

    now = datetime.datetime.now().date()

    results = {
        "NEW": [],
        "STABLE": [],
        "ESCALATED": [],
        "FLAPPING": [],
        "DORMANT": [],
    }

    current = current_snapshot.get("subdomains", {})
    previous = previous_snapshot.get("subdomains", {}) if previous_snapshot else {}

    for sub, data in current.items():
        if sub not in previous:
            results["NEW"].append(sub)
            continue

        prev = previous[sub]

        # Escalada de impacto
        if data.get("impact", 0) > prev.get("impact", 0):
            results["ESCALATED"].append(sub)
            continue

        # Estável
        if data.get("impact") == prev.get("impact"):
            results["STABLE"].append(sub)

    # Dormant: estava antes mas não aparece agora
    for sub in previous:
        if sub not in current:
            last_seen = previous[sub].get("last_seen")
            if last_seen:
                last_seen_date = datetime.datetime.strptime(
                    last_seen, "%Y-%m-%d"
                ).date()
                if (now - last_seen_date).days >= 2:
                    results["DORMANT"].append(sub)

    return results
