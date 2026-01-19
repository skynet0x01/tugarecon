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
tuga_scan_diff.py

Responsabilidade:
- Carregar resultados semânticos de scans anteriores
- Comparar dois scans por data (diff temporal)
- Identificar:
    • subdomínios novos
    • subdomínios removidos
    • subdomínios alterados (score ou tags)
- Exportar o diff para JSON
- Descobrir automaticamente o scan anterior mais recente

Este módulo é um pilar da "memória histórica" do TugaRecon.
É usado por utils/tuga_save.py e pelo motor de inteligência temporal.
"""

import json
import os
from typing import Dict, List, Optional


# --------------------------------------------------------------------------------------------------
def _safe_load_json(path: str) -> List[dict]:
    """
    Carrega um ficheiro JSON de forma segura.
    Retorna lista vazia se o ficheiro não existir ou estiver inválido.
    """
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


# --------------------------------------------------------------------------------------------------
def load_scan(target: str, date: str) -> List[dict]:
    """
    Carrega os resultados semânticos de um scan específico.
    """
    path = os.path.join("results", target, date, "semantic_results.json")
    return _safe_load_json(path)


# --------------------------------------------------------------------------------------------------
def diff_scans(target: str, old_date: str, new_date: str) -> Dict[str, list]:
    """
    Compara dois scans por data para um determinado target.

    Retorna um dicionário com:
      - new: subdomínios encontrados apenas no scan mais recente
      - removed: subdomínios que desapareceram desde o scan anterior
      - updated: subdomínios cujo impact_score ou tags mudaram
    """
    old_path = os.path.join("results", target, old_date, "semantic_results.json")
    new_path = os.path.join("results", target, new_date, "semantic_results.json")

    old_data = _safe_load_json(old_path)
    new_data = _safe_load_json(new_path)

    if not old_data or not new_data:
        return {"new": [], "removed": [], "updated": []}

    old_results = {r.get("subdomain"): r for r in old_data if "subdomain" in r}
    new_results = {r.get("subdomain"): r for r in new_data if "subdomain" in r}

    diff = {"new": [], "removed": [], "updated": []}

    # Detectar novos e alterados
    for sub, r in new_results.items():
        if sub not in old_results:
            diff["new"].append(r)
        else:
            old_r = old_results[sub]

            old_score = old_r.get("impact_score", 0)
            new_score = r.get("impact_score", 0)

            old_tags = set(old_r.get("tags", []))
            new_tags = set(r.get("tags", []))

            if old_score != new_score or old_tags != new_tags:
                diff["updated"].append({
                    "subdomain": sub,
                    "old_score": old_score,
                    "new_score": new_score,
                    "old_tags": list(old_tags),
                    "new_tags": list(new_tags),
                })

    # Detectar removidos
    for sub, r in old_results.items():
        if sub not in new_results:
            diff["removed"].append(r)

    return diff


# --------------------------------------------------------------------------------------------------
def export_diff(diff: Dict[str, list], target: str, date: str) -> str:
    """
    Exporta o diff de scans para JSON.
    """
    base = os.path.join("results", target, date)
    os.makedirs(base, exist_ok=True)

    path = os.path.join(base, "scan_diff.json")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(diff, f, indent=2, ensure_ascii=False)

    return path


# --------------------------------------------------------------------------------------------------
def get_previous_scan_date(target: str, today: str) -> Optional[str]:
    """
    Descobre automaticamente a data do scan anterior mais recente
    para um determinado target.
    """
    base = os.path.join("results", target)
    if not os.path.exists(base):
        return None

    dates = sorted(
        d for d in os.listdir(base)
        if d < today and os.path.isdir(os.path.join(base, d))
    )

    return dates[-1] if dates else None
