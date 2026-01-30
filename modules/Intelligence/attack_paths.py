from collections import deque


def infer_attack_paths(results, graph, max_depth=4):
    """
    Returns ranked attack paths leading to crown jewels.
    Output: pure structured data. No prints. No side effects.
    """

    nodes = {r["subdomain"]: r for r in results}
    paths = []

    # Entry points: onde um atacante pode começar
    entry_points = [
        r for r in results
        if r.get("attack_surface", {}).get("entry_point") is True
    ]

    for start in entry_points:
        queue = deque()
        queue.append((
            start["subdomain"],
            [start["subdomain"]],
            start["attack_surface"]["cost"]
        ))

        visited = set()

        while queue:
            current, path, cost = queue.popleft()

            if current in visited:
                continue
            visited.add(current)

            if len(path) > max_depth:
                continue

            node = nodes.get(current)
            if not node:
                continue

            # Crown jewel reached (but not trivial self-path)
            if node["attack_surface"].get("crown_jewel") and len(path) > 1:
                paths.append({
                    "path": path,
                    "total_cost": cost,
                    "final_impact": node.get("impact_score", 0),
                    "confidence": _confidence_from_path(path, nodes)
                })
                continue

            for neighbor in graph.get(current, []):
                if neighbor not in nodes:
                    continue

                n = nodes[neighbor]
                edge_cost = n["attack_surface"]["cost"]

                # Trust boundary bonus: external → internal
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

    # Ranking ofensivo: mais barato primeiro, mais impacto depois
    return sorted(
        paths,
        key=lambda p: (p["total_cost"], -p["final_impact"])
    )


def _confidence_from_path(path, nodes):
    """
    Simple, explainable confidence model.
    """

    score = 0

    for sub in path:
        tags = set(t.lower() for t in nodes[sub].get("tags", []))

        if {"vpn", "auth"} & tags:
            score += 2
        if {"admin", "infra", "internal"} & tags:
            score += 1
        if {"prod", "production"} & tags:
            score += 1

    if score >= 5:
        return "HIGH"
    if score >= 3:
        return "MEDIUM"
    return "LOW"
