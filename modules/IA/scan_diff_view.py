# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# Module: modules/IA/scan_diff_view.py
# --------------------------------------------------------------------------------------------------

import copy
from utils.tuga_colors import G, Y, R, W


# --------------------------------------------------------------------------------------------------
# Mapa de prioridade para ordenação numérica.
# Quanto maior o número, maior a criticidade.
# --------------------------------------------------------------------------------------------------
PRIORITY_ORDER = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4
}

# Prioridades que queremos efetivamente mostrar no output
DISPLAY_PRIORITIES = ["CRITICAL", "HIGH", "MEDIUM"]


# --------------------------------------------------------------------------------------------------
def normalize_priority(p: str) -> str:
    """
    Normaliza a prioridade para uppercase.
    Se não existir, assume LOW por padrão.
    """
    return (p or "LOW").upper()


# --------------------------------------------------------------------------------------------------
def sort_by_priority_then_impact(items: list[dict]) -> list[dict]:
    """
    Ordena uma lista de registos por:
        1) prioridade (decrescente)
        2) impact_score ou impact (decrescente)

    Itens com prioridade desconhecida recebem peso 0.
    """
    return sorted(
        items,
        key=lambda r: (
            -PRIORITY_ORDER.get(normalize_priority(r.get("priority")), 0),
            -r.get("impact_score", r.get("impact", 0))
        )
    )


# --------------------------------------------------------------------------------------------------
def is_relevant_priority(priority: str) -> bool:
    """
    Verifica se a prioridade é MEDIUM ou superior.
    """
    if not priority:
        return False

    return PRIORITY_ORDER.get(priority.upper(), 0) >= PRIORITY_ORDER["MEDIUM"]


# --------------------------------------------------------------------------------------------------
def print_scan_diff(diff: dict):
    """
    Renderiza diferenças entre scans de forma legível.

    Estrutura esperada:
        diff = {
            "new": [...],
            "updated": [...],
            "removed": [...]
        }

    Apenas mostra NEW e UPDATED com prioridade >= MEDIUM.
    REMOVED é sempre mostrado.
    """

    if not diff:
        print("[Δ] No differences detected.\n")
        return

    MIN_PRIORITY = PRIORITY_ORDER["MEDIUM"]

    # --------------------------------------------------------------------------------------------------
    def is_visible(record: dict) -> bool:
        """
        Define se um registo deve ser mostrado
        com base na prioridade mínima.
        """
        p = normalize_priority(record.get("priority"))
        return PRIORITY_ORDER.get(p, 1) >= MIN_PRIORITY

    # Filtrar apenas o que é relevante
    new = [r for r in diff.get("new", []) if is_visible(r)]
    updated = [r for r in diff.get("updated", []) if is_visible(r)]
    removed = diff.get("removed", [])  # removidos são sempre mostrados

    # --------------------------------------------------------------------------------------------------
    # Construção de resumo estatístico por prioridade
    # --------------------------------------------------------------------------------------------------
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

    # Se nada relevante existir
    if not new and not updated and not removed:
        print(Y + "[✓] No relevant changes (MEDIUM+)\n" + W)
        return

    # --------------------------------------------------------------------------------------------------
    # REMOVED
    # --------------------------------------------------------------------------------------------------
    if removed:
        print(R + "\n[!] Removed since last scan" + W)
        print("-" * 70)

        for r in removed:
            priority = normalize_priority(r.get("priority", "LOW"))
            sub = r.get("subdomain", "unknown")
            print(f" • {sub} [{priority}]")

    # --------------------------------------------------------------------------------------------------
    # NEW + UPDATED combinados
    # --------------------------------------------------------------------------------------------------
    combined = []

    # Clonar para não modificar estrutura original
    for r in new:
        rr = copy.deepcopy(r)
        rr["_change"] = "NEW"
        combined.append(rr)

    for r in updated:
        rr = copy.deepcopy(r)
        rr["_change"] = "UPDATED"
        combined.append(rr)

    # Ordenar por prioridade e impacto
    combined = sort_by_priority_then_impact(combined)

    current_priority = None

    for r in combined:
        priority = normalize_priority(r.get("priority"))

        # Só mostrar prioridades relevantes
        if priority not in DISPLAY_PRIORITIES:
            continue

        # Cabeçalho por grupo de prioridade
        if priority != current_priority:
            print(f"\n[ {priority} ]")
            print("--------------------------------------------------------------------------------")
            current_priority = priority

        impact = r.get("impact_score", r.get("impact", 0))
        tags = ",".join(r.get("tags", [])) or "-"
        change = r.get("_change", "")
        sub = r.get("subdomain", "unknown")

        # Cor dinâmica por severidade
        color = (
            R if priority == "CRITICAL"
            else Y if priority == "HIGH"
            else G
        )

        print(
            f" {color}•{W} {sub:<38} "
            f"impact={impact:<3} "
            f"tags={tags} "
            f"[{change}]"
        )
