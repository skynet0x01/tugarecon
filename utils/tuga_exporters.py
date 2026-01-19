# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
"""
tuga_exporters.py

Responsabilidade:
- Exportar resultados semânticos para JSON canónico
- Gerar listas de alvos por prioridade (CRITICAL / HIGH)
- Servir como ponto único de saída estruturada do motor IA

Este módulo é consumido por utils/tuga_save.py
e por futuros módulos de reporting, timeline e dashboards.
"""

import json
import os
import datetime
from typing import List, Dict


# --------------------------------------------------------------------------------------------------
def export_json(results: List[dict], target: str, date: str,
                filename: str = "semantic_results.json") -> str:
    """
    Exporta resultados semânticos para JSON canónico.
    """
    base = os.path.join("results", target, date)
    os.makedirs(base, exist_ok=True)

    path = os.path.join(base, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return path


# --------------------------------------------------------------------------------------------------
def export_priority_lists(results: List[dict], target: str) -> Dict[str, str]:
    """
    Gera ficheiros de alvos por prioridade (CRITICAL / HIGH).

    Retorna:
        dict: { "critical": path, "high": path }
    """
    date = str(datetime.datetime.now().date())
    base = os.path.join("results", target, date)
    os.makedirs(base, exist_ok=True)

    buckets = {
        "CRITICAL": [],
        "HIGH": []
    }

    for r in results:
        p = r.get("priority")
        if p in buckets:
            buckets[p].append(r)

    exported = {}

    for level, items in buckets.items():
        if not items:
            continue

        path = os.path.join(base, f"{level.lower()}_targets.txt")

        with open(path, "w", encoding="utf-8") as f:
            for r in items:
                sub = r.get("subdomain", "")
                score = r.get("impact_score", 0)
                tags = ",".join(r.get("tags", []))

                f.write(
                    f"{sub:<65} "
                    f"impact={score:>3} "
                    f"tags={tags}\n"
                )

        exported[level.lower()] = path

    return exported
