# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# Model: modules/intelligence/attack_paths.py
# License: GNU GPLv3
# Model: models/IA/heuristics.py
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

# Estrutura eficiente para BFS (Breadth-First Search)
# Permite adicionar e remover elementos das extremidades em O(1)
from collections import deque


def infer_attack_paths(results, graph, max_depth=4):
    """
    Inferir e classificar caminhos de ataque até ativos críticos (crown jewels).

    Parâmetros:
        results -> lista de dicionários com metadados por subdomínio
        graph   -> grafo de conectividade {node: [neighbors]}
        max_depth -> profundidade máxima de exploração

    Retorna:
        Lista ordenada de caminhos com custo total, impacto final e confiança.
        (Função pura: não imprime nem altera estado externo)
    """

    # Criar índice rápido por subdomínio
    # Permite acesso O(1) a cada nó
    nodes = {r["subdomain"]: r for r in results}

    # Lista final de caminhos encontrados
    paths = []

    # ---------------------------
    # Identificar pontos de entrada
    # ---------------------------
    # Entry point = superfície exposta onde um atacante pode iniciar
    entry_points = [
        r for r in results
        if r.get("attack_surface", {}).get("entry_point") is True
    ]

    # Para cada ponto inicial identificado
    for start in entry_points:

        # Fila para BFS: (nó atual, caminho percorrido, custo acumulado)
        queue = deque()
        queue.append((
            start["subdomain"],
            [start["subdomain"]],
            start["attack_surface"]["cost"]
        ))

        # Conjunto para evitar revisitar nós
        visited = set()

        # ---------------------------
        # Exploração do grafo (BFS)
        # ---------------------------
        while queue:
            current, path, cost = queue.popleft()

            # Evitar loops
            if current in visited:
                continue
            visited.add(current)

            # Limitar profundidade (controle de explosão combinatória)
            if len(path) > max_depth:
                continue

            node = nodes.get(current)
            if not node:
                continue

            # ---------------------------
            # Se atingimos um crown jewel
            # ---------------------------
            # Evita considerar caminho trivial (nó inicial sozinho)
            if node["attack_surface"].get("crown_jewel") and len(path) > 1:
                paths.append({
                    "path": path,
                    "total_cost": cost,
                    "final_impact": node.get("impact_score", 0),
                    "confidence": _confidence_from_path(path, nodes)
                })
                continue

            # ---------------------------
            # Explorar vizinhos
            # ---------------------------
            for neighbor in graph.get(current, []):
                if neighbor not in nodes:
                    continue

                n = nodes[neighbor]

                # Custo do próximo passo
                edge_cost = n["attack_surface"]["cost"]

                # Bónus heurístico:
                # Se atravessamos fronteira de confiança
                # (external → internal),
                # reduzimos custo porque isso é ofensivamente valioso
                if (
                    node.get("exposure") == "external"
                    and n.get("exposure") == "internal"
                ):
                    edge_cost -= 10

                queue.append((
                    neighbor,
                    path + [neighbor],
                    cost + edge_cost
                ))

    # ---------------------------
    # Ordenação ofensiva
    # ---------------------------
    # Primeiro menor custo
    # Depois maior impacto
    return sorted(
        paths,
        key=lambda p: (p["total_cost"], -p["final_impact"])
    )


def _confidence_from_path(path, nodes):
    """
    Modelo simples e explicável de confiança.

    Atribui score com base nas tags encontradas ao longo do caminho.
    Quanto mais sensíveis as tags, maior confiança no cenário.
    """

    score = 0

    for sub in path:
        # Normalização para lowercase
        tags = set(t.lower() for t in nodes[sub].get("tags", []))

        # VPN/Auth aumentam probabilidade de movimento lateral relevante
        if {"vpn", "auth"} & tags:
            score += 2

        # Infraestrutura sensível
        if {"admin", "infra", "internal"} & tags:
            score += 1

        # Ambiente produtivo
        if {"prod", "production"} & tags:
            score += 1

    # Classificação simples por limiar
    if score >= 5:
        return "HIGH"
    if score >= 3:
        return "MEDIUM"
    return "LOW"
