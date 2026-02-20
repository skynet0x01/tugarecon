# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# Module: modules/intelligence/snapshot.py
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
import json
import os
from datetime import datetime

SNAPSHOT_NAME = "scan_snapshot.json"


def load_previous_snapshot(scan_dir: str) -> dict:
    path = os.path.join(scan_dir, SNAPSHOT_NAME)
    if not os.path.isfile(path):
        return {}

    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_snapshot(scan_dir: str, snapshot: dict):
    path = os.path.join(scan_dir, SNAPSHOT_NAME)
    with open(path, "w") as f:
        json.dump(snapshot, f, indent=2, sort_keys=True)


def build_snapshot(results: list, previous: dict | None = None) -> dict:
    """
    results = lista de subdomínios classificados
    previous = snapshot anterior (ou {})
    """

    now = datetime.utcnow().strftime("%Y-%m-%d")
    previous = previous or {}

    subdomains = {}

    for r in results:
        sub = r["subdomain"]

        # Agora olhamos corretamente para previous["subdomains"]
        old = previous.get("subdomains", {}).get(sub, {})

        subdomains[sub] = {
            "subdomain": sub,
            "priority": r.get("priority", "LOW"),
            "impact": r.get("impact", r.get("impact_score", 0)),
            "impact_score": r.get("impact_score", r.get("impact", 0)),
            "tags": r.get("tags", []),

            # Estado temporal (fundamental!)
            "state": r.get("state", "NEW"),

            # Histórico
            "first_seen": old.get("first_seen", now),
            "last_seen": now,
            "seen_count": old.get("seen_count", 0) + 1
        }

    return {
        "subdomains": subdomains,
        "generated_at": now
    }
