import json
import os
from threading import Lock

# Caminho do ficheiro de memória global
MEMORY_FILE = os.path.join("data", "global_ia_memory.json")

# Lock para evitar corrupção em execuções concorrentes
_memory_lock = Lock()


def _initialize_memory():
    """
    Cria a estrutura base do ficheiro de memória,
    caso ainda não exista.
    """
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.isfile(MEMORY_FILE):
        base_structure = {
            "tokens": {},
            "patterns": {}
        }

        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(base_structure, f, indent=4)


def load_memory():
    """
    Carrega a memória global do disco.
    """
    _initialize_memory()

    with _memory_lock:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)


def save_memory(memory_data):
    """
    Guarda a memória no disco de forma segura.
    """
    with _memory_lock:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory_data, f, indent=4)


def update_token_stats(tokens, severity=None, domain=None):
    """
    Atualiza estatísticas globais dos tokens encontrados.

    tokens: lista de strings
    severity: 'critical', 'high', 'medium', etc.
    domain: domínio onde foi encontrado
    """
    if not tokens:
        return

    memory = load_memory()

    for token in tokens:
        if token not in memory["tokens"]:
            memory["tokens"][token] = {
                "seen": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "domains": []
            }

        memory["tokens"][token]["seen"] += 1

        if severity in memory["tokens"][token]:
            memory["tokens"][token][severity] += 1

        if domain and domain not in memory["tokens"][token]["domains"]:
            memory["tokens"][token]["domains"].append(domain)

    save_memory(memory)


def get_token_weight(token):
    """
    Calcula um peso simples baseado na frequência
    e na severidade histórica do token.
    """
    memory = load_memory()

    if token not in memory["tokens"]:
        return 1.0  # peso neutro

    data = memory["tokens"][token]

    # Fórmula simples e interpretável
    weight = (
        data["seen"] * 0.5 +
        data["critical"] * 3 +
        data["high"] * 2 +
        data["medium"] * 1
    )

    # Normalização mínima
    return max(weight, 1.0)
