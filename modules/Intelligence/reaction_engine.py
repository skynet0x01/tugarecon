# ----------------------------------------------------------------------------------------------------------
# reaction_engine.py
# Author: Skynet0x01
# Description:
#   Este módulo é responsável por executar reacções automáticas em subdomínios
#   com base em seu estado temporal, impacto e tags semânticas (ICS/SCADA awareness).
#   Inclui reações HTTP, TLS e Headers. Gera metadados e logs detalhados.
# ----------------------------------------------------------------------------------------------------------

import os
import json
import traceback

from modules.Intelligence.reactions.tls_reaction import run_tls_reaction
from modules.Intelligence.reactions.headers_reaction import run_headers
from modules.Intelligence.reactions.httpx_reaction import run_httpx
from modules.IA.heuristics import SCADA_TOKENS

# Map of reaction names to functions
# Ordem importa: HTTPX primeiro, depois TLS, depois Headers
REACTION_MAP = {
    "HTTPX": [run_httpx, run_tls_reaction, run_headers],
    "HTTP": [run_httpx],
    "DEEP_HTTP_PROBE": [run_httpx, run_tls_reaction, run_headers],
    "HEADER_ANALYSIS": [run_headers],
    "TLS_ONLY": [run_tls_reaction],
    "WATCH": [],  # apenas monitorização
}

def react(entry: dict, output_dir: str):
    """
    Executa reacções para um subdomínio.
    Cria metadata.json e executa cada reacção definida.
    """
    sub = entry["subdomain"]
    action = entry["action"]

    # Subdiretório seguro para o subdomínio
    sub_dir = os.path.join(output_dir, sub.replace("/", "_"))
    os.makedirs(sub_dir, exist_ok=True)

    # Metadata incluindo tags e prioridade, especialmente para ICS/SCADA
    metadata = {
        "subdomain": sub,
        "state": entry.get("state"),
        "impact": entry.get("impact"),
        "score": entry.get("score"),
        "priority": entry.get("priority"),
        "tags": entry.get("tags", []),
        "action": action,
    }

    # Salva metadata
    with open(os.path.join(sub_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)

    # Executa cada reacção
    for reaction in REACTION_MAP.get(action, []):
        try:
            reaction(sub, sub_dir)
        except Exception:
            with open(os.path.join(sub_dir, "error.log"), "a") as f:
                f.write(traceback.format_exc() + "\n")