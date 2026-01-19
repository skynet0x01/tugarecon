# --------------------------------------------------------------------------------------------------
# TugaRecon - Unified Reaction & Decision Engine
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

import os
import json
import traceback

# Import reaction modules
from modules.Intelligence.reactions.tls_reaction import run_tls_reaction
from modules.Intelligence.reactions.headers_reaction import run_headers
from modules.Intelligence.reactions.httpx_reaction import run_httpx

# Import scoring & heuristics
from modules.IA.impact_score import SCADA_TOKENS, compute_impact_score

# --------------------------------------------------------------------------------------------------
# Map of reaction names to functions
# Order matters: HTTPX runs first, then TLS, then headers
REACTION_MAP = {
    "HTTPX": [run_httpx, run_tls_reaction, run_headers],
    "HTTP": [run_httpx],
    "DEEP_HTTP_PROBE": [run_httpx, run_tls_reaction, run_headers],
    "HEADER_ANALYSIS": [run_headers],
    "TLS_ONLY": [run_tls_reaction],
    "WATCH": [],   # placeholder for monitoring-only reactions
    "IGNORE": [],
}

# --------------------------------------------------------------------------------------------------
def react(entry: dict, output_dir: str):
    """
    Execute reactions for a given subdomain entry.
    - Generates metadata.json per subdomain
    - Runs each reaction sequentially
    - Logs errors per subdomain
    """
    sub = entry.get("subdomain")
    action = entry.get("action", "IGNORE")

    if not sub:
        return

    # Safe subdirectory for results
    sub_dir = os.path.join(output_dir, sub.replace("/", "_"))
    os.makedirs(sub_dir, exist_ok=True)

    # Metadata includes scoring info and tags
    metadata = {
        "subdomain": sub,
        "state": entry.get("state"),
        "impact_score": entry.get("impact_score"),
        "priority": entry.get("priority"),
        "tags": entry.get("tags", []),
        "action": action,
    }

    # Save metadata
    try:
        with open(os.path.join(sub_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
    except Exception:
        with open(os.path.join(sub_dir, "error.log"), "a") as f:
            f.write("Failed to write metadata.json\n")
            f.write(traceback.format_exc() + "\n")

    # Execute reactions safely
    for reaction in REACTION_MAP.get(action, []):
        try:
            reaction(sub, sub_dir)
        except Exception:
            with open(os.path.join(sub_dir, "error.log"), "a") as f:
                f.write(f"[{reaction.__name__}] failed\n")
                f.write(traceback.format_exc() + "\n")

# --------------------------------------------------------------------------------------------------
def decide_action(entry: dict) -> str:
    """
    Decide which reaction to trigger based on:
    - Semantic tags (SCADA / IT / infra / business)
    - Impact score
    - Temporal state
    - ICS override rules
    """
    # Ensure semantic scoring is computed
    entry = compute_impact_score(entry)

    score = entry.get("impact_score", 0)
    tags = set(entry.get("tags", []))
    temporal_state = entry.get("state", "")

    # ICS/SCADA override: always deep HTTPX + TLS + headers
    if tags & SCADA_TOKENS:
        return "HTTPX"

    # High escalation events
    if temporal_state == "ESCALATED":
        return "HTTPX"

    # New assets with medium+ impact
    if temporal_state == "NEW":
        if score >= 20:
            return "DEEP_HTTP_PROBE"
        return "WATCH"

    # Flapping assets
    if temporal_state == "FLAPPING":
        return "WATCH"

    # Stable assets with high impact may still require monitoring
    if temporal_state == "STABLE":
        if score >= 50:
            return "WATCH"
        return "IGNORE"

    # Dormant or low-risk
    if temporal_state == "DORMANT":
        return "IGNORE"

    # Default fallback
    return "IGNORE"

# --------------------------------------------------------------------------------------------------
def process_entry(entry: dict, output_dir: str):
    """
    Convenience function:
    - Decide the action
    - Set it in the entry
    - Execute reactions
    """
    entry["action"] = decide_action(entry)
    react(entry, output_dir)
    return entry

