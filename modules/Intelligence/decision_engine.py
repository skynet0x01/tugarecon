# ----------------------------------------------------------------------------------------------------------
# decide_action.py
# Author: Skynet0x01
# Description:
#   Este módulo unifica a lógica de decisão de ações de scan e reacção.
#   Considera impacto, estado temporal e tags semânticas (ex: SCADA/ICS).
#   Retorna tupla (scan_action, reaction_action)
# ----------------------------------------------------------------------------------------------------------

from modules.IA.heuristics import SCADA_TOKENS

def decide_action(subdomain: str, impact: int, temporal_state: str, temporal_score: int, tags: set[str] = set()):
    """
    Decide ações de scan e reacção para um subdomínio.

    Parâmetros:
    - subdomain: nome do subdomínio
    - impact: pontuação de impacto (0-100)
    - temporal_state: NEW, ESCALATED, FLAPPING, STABLE, DORMANT
    - temporal_score: pontuação temporal (opcional)
    - tags: conjunto de tags semânticas (ex: ICS/SCADA)

    Retorna:
    - (scan_action: str, reaction_action: str)
    """

    # ICS/SCADA override: sempre executar scan profundo e reacções completas
    if tags & SCADA_TOKENS:
        return "DEEP_SCAN", "HTTPX"

    # Estados temporais
    if temporal_state == "ESCALATED":
        return "PRIORITY_RESCAN", "HTTPX"

    if temporal_state == "NEW":
        if impact >= 20:
            return "DEEP_SCAN", "HTTP"
        return "WATCH", "WATCH"

    if temporal_state == "FLAPPING":
        return "WATCH", "WATCH"

    if temporal_state == "STABLE":
        if impact >= 50:
            return "WATCH", "WATCH"
        return "IGNORE", "IGNORE"

    if temporal_state == "DORMANT":
        return "IGNORE", "IGNORE"

    # Default fallback
    return "IGNORE", "IGNORE"