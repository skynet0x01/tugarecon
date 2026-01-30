# --------------------------------------------------------------------------------------------------
# TugaRecon - Impact Graph & Propagation Engine
# Author: Skynet0x01 2020-2026
# License: GNU GPLv3
# --------------------------------------------------------------------------------------------------

from collections import defaultdict


# Heurísticas simples e explicáveis
DEPENDENCY_RULES = [
    ("auth", "api"),
    ("api", "billing"),
    ("api", "payments"),
    ("vpn", "internal"),
    ("admin", "internal"),
    ("cicd", "cloud"),
]

CONTROL_RULES = {"auth", "admin", "identity", "secrets"}
LATERAL_RULES = {"vpn", "jump", "bastion", "internal"}


def build_impact_graph(entries):
    """
    Build implicit dependency graph based on tags and naming.
    """
    graph = defaultdict(set)

    for src in entries:
        src_name = src.get("subdomain")
        src_tags = set(src.get("tags", []))

        for dst in entries:
            dst_name = dst.get("subdomain")
            dst_tags = set(dst.get("tags", []))

            if src is dst:
                continue

            # Explicit dependency rules
            for a, b in DEPENDENCY_RULES:
                if a in src_tags and b in dst_tags:
                    graph[src_name].add(dst_name)

            # Control-plane dominance
            if src_tags & CONTROL_RULES and dst_tags - src_tags:
                graph[src_name].add(dst_name)

            # Lateral movement potential
            if src_tags & LATERAL_RULES and "internal" in dst_tags:
                graph[src_name].add(dst_name)

    return graph


def propagate_impact(entries, graph, decay=0.6):
    """
    Propagate impact through the graph with decay.
    """
    index = {e["subdomain"]: e for e in entries}

    for src_name, targets in graph.items():
        src = index.get(src_name)
        if not src:
            continue

        base = src.get("impact_score", 0)
        propagated = int(base * decay)

        paths = []

        for dst_name in targets:
            dst = index.get(dst_name)
            if not dst:
                continue

            # Raise impact only if higher
            if propagated > dst.get("impact_score", 0):
                dst["impact_score"] = min(100, propagated)
                dst["priority"] = _priority_from_score(dst["impact_score"])
                paths.append(f"{src_name} → {dst_name}")

        if paths:
            src["blast_radius"] = {
                "affected_assets": len(paths),
                "propagated_impact": propagated,
                "paths": paths
            }

    return entries


def _priority_from_score(score: int) -> str:
    if score >= 90:
        return "CRITICAL"
    elif score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    return "LOW"
