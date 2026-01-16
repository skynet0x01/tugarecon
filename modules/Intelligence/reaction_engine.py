# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
import os
import json

from modules.Intelligence.reactions.tls_reaction import run_tls_reaction
from modules.Intelligence.reactions.headers_reaction import run_headers
from modules.Intelligence.reactions.httpx_reaction import run_httpx


REACTION_MAP = {
    "HTTPX": [run_httpx, run_tls_reaction, run_headers],
    "HTTP": [run_httpx],
    "DEEP_HTTP_PROBE": [run_httpx, run_tls_reaction, run_headers],
    "HEADER_ANALYSIS": [run_headers],
    "TLS_ONLY": [run_tls_reaction],
}

def react(entry, output_dir):
    sub = entry["subdomain"]
    action = entry["action"]

    sub_dir = os.path.join(output_dir, sub.replace("/", "_"))
    os.makedirs(sub_dir, exist_ok=True)

    metadata = {
        "subdomain": sub,
        "state": entry["state"],
        "impact": entry["impact"],
        "score": entry["score"],
        "action": action,
    }

    with open(os.path.join(sub_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    for reaction in REACTION_MAP.get(action, []):
        try:
            reaction(sub, sub_dir)
        except Exception as e:
            with open(os.path.join(sub_dir, "error.log"), "a") as f:
                f.write(str(e) + "\n")



# ----------------------------------------------------------------------------------------------------------
def decide_action(subdomain, impact, temporal_state, temporal_score):
    if temporal_state == "ESCALATED":
        return "HTTPX"

    if temporal_state == "NEW" and impact >= 20:
        return "HTTP"

    if temporal_state == "FLAPPING":
        return "WATCH"

    return "IGNORE"
