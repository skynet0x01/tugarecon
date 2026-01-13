def compute_temporal_score(subdomain_data, temporal_state):
    """
    Calcula score final usando impacto + comportamento temporal
    """

    impact = subdomain_data.get("impact", 0)
    score = impact

    if temporal_state == "NEW":
        score += 15

    elif temporal_state == "ESCALATED":
        score += 20

    elif temporal_state == "FLAPPING":
        score += 10

    elif temporal_state == "STABLE":
        score += 0

    elif temporal_state == "DORMANT":
        score -= 20

    # limites de segurança
    if score < 0:
        score = 0
    if score > 100:
        score = 100

    return score
