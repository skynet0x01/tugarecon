import datetime

def compute_temporal_score(subdomain_data, temporal_state):
    """
    Calcula score final usando impacto + comportamento temporal + decay temporal
    """

    impact = subdomain_data.get("impact", 0)
    score = impact

    # ───── Ajuste por estado temporal ─────
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

    # ───── Decay temporal (tempo desde last_seen) ─────
    last_seen = subdomain_data.get("last_seen")
    if last_seen:
        try:
            last_seen_date = datetime.datetime.strptime(
                last_seen, "%Y-%m-%d"
            ).date()

            days_passed = (datetime.date.today() - last_seen_date).days

            # regra simples: -2 pontos por dia após o 1.º
            if days_passed > 1:
                score -= min(days_passed * 2, 40)

        except Exception:
            pass  # nunca quebrar o pipeline por datas

    # ───── limites de segurança ─────
    if score < 0:
        score = 0
    if score > 100:
        score = 100

    return score

