# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
import json
import os
import datetime

def export_json(results: list, target: str, date: str,
                filename="semantic_results.json"):
    base = f"results/{target}/{date}"
    os.makedirs(base, exist_ok=True)

    path = os.path.join(base, filename)

    with open(path, "w") as f:
        json.dump(results, f, indent=2)

    return path


def export_priority_lists(results: list, target: str):
    date = str(datetime.datetime.now().date())
    base = f"results/{target}/{date}"
    os.makedirs(base, exist_ok=True)

    buckets = {
        "CRITICAL": [],
        "HIGH": []
    }

    for r in results:
        p = r.get("priority")
        if p in buckets:
            buckets[p].append(r)

    for level, items in buckets.items():
        if not items:
            continue

        path = os.path.join(base, f"{level.lower()}_targets.txt")
        with open(path, "w") as f:
            for r in items:
                f.write(
                    f"{r['subdomain']:<65} "
                    f"impact={r['impact_score']:>3} "
                    f"tags={','.join(r['tags'])}\n"
                )
