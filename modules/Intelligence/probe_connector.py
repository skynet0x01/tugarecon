# --------------------------------------------------------------------------------------------------
# TugaRecon – Probe to Semantic Connector
# Author: Skynet0x01 2020-2026
# License: GNU GPLv3
# --------------------------------------------------------------------------------------------------

import json
import os
from datetime import datetime

# Mapeamento heurístico simples por título / servidor
SERVICE_TAGS = {
    "nginx": ["web", "infra"],
    "apache": ["web", "infra"],
    "cloudflare": ["cdn", "infra"],
    "iis": ["web", "windows"],
    "tomcat": ["java", "app"],
    "api": ["api"],
    "admin": ["admin", "critical"],
    "vpn": ["vpn", "network"],
}

def infer_tags(service):
    tags = set(["web"])
    server = service.get("server", "").lower()
    title = service.get("title", "").lower()
    url = service.get("url", "").lower()

    for key, mapped in SERVICE_TAGS.items():
        if key in server or key in title or key in url:
            tags.update(mapped)

    if service.get("scheme") == "https":
        tags.add("tls")

    return list(tags)

def base_impact_score(service, tags):
    score = 5

    if "admin" in tags:
        score += 25
    if "vpn" in tags:
        score += 20
    if "api" in tags:
        score += 15
    if "critical" in tags:
        score += 30
    if service.get("scheme") == "https":
        score += 5

    status = service.get("status", 0)
    if status in [401, 403]:
        score += 10
    if status >= 500:
        score += 5

    return score


def convert_services_to_semantic(services_file, output_file):
    if not os.path.isfile(services_file):
        raise FileNotFoundError(services_file)

    with open(services_file) as f:
        services = json.load(f)

    semantic_entries = []

    for svc in services:
        # tags podem ser inferidas como antes
        tags = svc.get("tags", [])

        # cálculo simplificado do impacto
        status = svc.get("status", 0)
        if 200 <= status < 300:
            score = 50
        elif 300 <= status < 400:
            score = 30
        elif 400 <= status < 600:
            score = 10
        else:
            score = 5

        # se tiver tags críticas, aumenta o impacto
        if "admin" in tags or "login" in tags:
            score += 20
        elif tags:
            score += 10

        entry = {
            "subdomain": svc.get("host"),
            "url": svc.get("url"),
            "status": status,
            "title": svc.get("title"),
            "server": svc.get("server"),
            "scheme": svc.get("scheme"),
            "redirected": svc.get("redirected"),
            "tags": tags,
            "impact_score": score,
            "state": "NEW",
            "source": "probe",
            "first_seen": datetime.utcnow().isoformat() + "Z"
        }

        semantic_entries.append(entry)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(semantic_entries, f, indent=2)

    print(f"[+] Converted {len(semantic_entries)} services to semantic entries")
