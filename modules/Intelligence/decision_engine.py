# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

def decide_action(subdomain, impact, temporal_state, temporal_score):
    """
    Decide ação operacional com base no estado temporal e impacto
    """

    if temporal_state == "ESCALATED":
        return "PRIORITY_RESCAN"

    if temporal_state == "NEW":
        if impact >= 20:
            return "DEEP_SCAN"
        return "WATCH"

    if temporal_state == "FLAPPING":
        return "WATCH"

    if temporal_state == "STABLE":
        if impact >= 50:
            return "WATCH"
        return "IGNORE"

    if temporal_state == "DORMANT":
        return "IGNORE"

    return "IGNORE"
