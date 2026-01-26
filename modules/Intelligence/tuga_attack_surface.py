# --------------------------------------------------------------------------------------------------
# TugaRecon – Attack Surface Engine (Enhanced)
# Author: Skynet0x01 2020-2026
# Enhanced by: Recon AI
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# --------------------------------------------------------------------------------------------------

import os
import json
from collections import defaultdict
from utils.tuga_colors import G, Y, R, W

# --------------------------------------------------------------------------------------------------
class TugaAttackSurface:

    CATEGORY_RISK = {
        "auth_panels": 5,
        "monitoring": 4,
        "api": 4,
        "mail": 3,
        "remote_access": 5,
        "non_prod": 2,
        "scada_ot": 5,
        "finance": 5,
        "health": 5,
        "government": 4,
        "ecommerce": 3,
        "admin": 5,
        "database": 5,
        "internal": 4,
        "cdn": 1,
        "web": 1,
    }

    def __init__(self, context_file, output_dir):
        self.context_file = context_file
        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

        self.context = {}
        self.surface = defaultdict(list)
        self.priority_targets = []

    # --------------------------------------------------------------------------------------------------
    def load_context(self):
        with open(self.context_file) as f:
            self.context = json.load(f)

    # --------------------------------------------------------------------------------------------------
    def classify(self, domain, entry):
        service = entry.get("service") or {}
        title = (service.get("title") or "").lower()
        flags = entry.get("flags", [])
        scheme = (service.get("scheme") or "").lower()

        d = domain.lower()

        # Painéis de autenticação
        if "login_panel" in flags or "login" in title or "auth" in d:
            return "auth_panels"

        # Monitoramento / dashboards
        if "grafana" in title or "kibana" in title or "monitor" in title:
            return "monitoring"

        # APIs
        if "api" in d or "api" in title:
            return "api"

        # Admin / backoffice
        if any(k in d for k in ["admin", "portal", "dashboard", "console"]):
            return "admin"

        # Email
        if any(k in d for k in ["mail", "smtp", "imap", "pop"]):
            return "mail"

        # VPN / acesso remoto
        if any(k in d for k in ["vpn", "remote", "rdp"]):
            return "remote_access"

        # Ambientes não-prod
        if any(k in d for k in ["dev", "test", "stage", "uat", "qa", "sandbox"]):
            return "non_prod"

        # SCADA / OT
        if any(k in d for k in ["scada", "plc", "hmi", "rtu", "ics"]):
            return "scada_ot"

        # Financeiro
        if any(k in d for k in ["bank", "corebank", "payment", "pos", "billing"]):
            return "finance"

        # Saúde
        if any(k in d for k in ["ehr", "emr", "hospital", "clinic", "lab"]):
            return "health"

        # Governo
        if any(k in d for k in ["gov", "portal", "financas", "tax"]):
            return "government"

        # E-commerce
        if any(k in d for k in ["shop", "store", "checkout", "cart"]):
            return "ecommerce"

        # Base de dados
        if any(k in d for k in ["db", "sql", "mongo", "redis", "postgres"]):
            return "database"

        # Interno
        if any(k in d for k in ["internal", "corp", "intranet"]):
            return "internal"

        # CDN / infra
        if any(k in d for k in ["cdn", "akamai", "cloudfront"]):
            return "cdn"

        return "web"

    # --------------------------------------------------------------------------------------------------
    def compute_risk(self, entry, category):
        base_risk = entry.get("risk_score", 0)
        impact = entry.get("impact_score", 0)
        cat_risk = self.CATEGORY_RISK.get(category, 1)

        # risco final = o maior entre impacto, categoria e risco prévio
        return max(base_risk, impact, cat_risk)

    # --------------------------------------------------------------------------------------------------
    def build_surface(self):
        for domain, entry in self.context.items():
            category = self.classify(domain, entry)
            risk = self.compute_risk(entry, category)

            entry["risk_score"] = risk
            entry["category"] = category

            self.surface[category].append({
                "domain": domain,
                "risk_score": risk,
                "impact_score": entry.get("impact_score", 0)
            })

            if risk >= 4:
                self.priority_targets.append(domain)

    # --------------------------------------------------------------------------------------------------
    def save_outputs(self):
        # JSON estruturado
        with open(os.path.join(self.output_dir, "attack_surface.json"), "w") as f:
            json.dump(self.surface, f, indent=2)

        # Priority targets
        with open(os.path.join(self.output_dir, "priority_targets.txt"), "w") as f:
            for d in sorted(set(self.priority_targets)):
                f.write(d + "\n")

        # Summary humano
        with open(os.path.join(self.output_dir, "attack_surface_summary.txt"), "w") as f:
            f.write("=== TugaRecon Attack Surface Summary ===\n\n")
            for cat, items in self.surface.items():
                f.write(f"[{cat.upper()}] ({len(items)})\n")
                for i in sorted(items, key=lambda x: x["risk_score"], reverse=True):
                    f.write(f"  - {i['domain']} | risk={i['risk_score']} | impact={i['impact_score']}\n")
                f.write("\n")

    # --------------------------------------------------------------------------------------------------
    def run(self):
        print(Y + "[*] Loading context..." + W)
        self.load_context()

        print(Y + "[*] Building attack surface..." + W)
        self.build_surface()

        self.save_outputs()

        print(G + "[+] Attack surface built successfully!" + W)
        print(G + f"[+] Categories: {len(self.surface)}" + W)
        print(G + f"[+] Priority targets: {len(self.priority_targets)}" + W)
        print(G + f"[+] Output in: {self.output_dir}" + W)


# # --------------------------------------------------------------------------------------------------
# # TugaRecon – Attack Surface Engine
# # Author: Skynet0x01 2020-2026
# # GitHub: https://github.com/skynet0x01/tugarecon
# # License: GNU GPLv3
# # Patent Restriction Notice:
# # No patents may be claimed or enforced on this software or any derivative.
# # Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# # --------------------------------------------------------------------------------------------------
#
# import os
# import json
# from collections import defaultdict
# from utils.tuga_colors import G, Y, R, W
#
# # --------------------------------------------------------------------------------------------------
# class TugaAttackSurface:
#
#     def __init__(self, context_file, output_dir):
#         self.context_file = context_file
#         self.output_dir = output_dir
#
#         os.makedirs(self.output_dir, exist_ok=True)
#
#         self.context = {}
#         self.surface = defaultdict(list)
#         self.priority_targets = []
#
#     # --------------------------------------------------------------------------------------------------
#     def load_context(self):
#         with open(self.context_file) as f:
#             self.context = json.load(f)
#
#     # --------------------------------------------------------------------------------------------------
#     def classify(self, domain, entry):
#         service = entry.get("service") or {}
#         title = (service.get("title") or "").lower()
#         flags = entry.get("flags", [])
#
#         if "login_panel" in flags:
#             return "auth_panels"
#         if "grafana_panel" in flags:
#             return "monitoring"
#         if "api" in domain:
#             return "api"
#         if any(k in domain for k in ["mail", "smtp", "imap", "pop"]):
#             return "mail"
#         if any(k in domain for k in ["vpn", "remote"]):
#             return "remote_access"
#         if any(k in domain for k in ["dev", "test", "stage"]):
#             return "non_prod"
#         return "web"
#
#     # --------------------------------------------------------------------------------------------------
#     def build_surface(self):
#         for domain, entry in self.context.items():
#             category = self.classify(domain, entry)
#             self.surface[category].append(domain)
#
#             if entry.get("risk_score", 0) >= 5:
#                 self.priority_targets.append(domain)
#
#     # --------------------------------------------------------------------------------------------------
#     def save_outputs(self):
#         with open(os.path.join(self.output_dir, "attack_surface.json"), "w") as f:
#             json.dump(self.surface, f, indent=2)
#
#         with open(os.path.join(self.output_dir, "priority_targets.txt"), "w") as f:
#             for d in sorted(set(self.priority_targets)):
#                 f.write(d + "\n")
#
#         with open(os.path.join(self.output_dir, "attack_surface_summary.txt"), "w") as f:
#             f.write("=== TugaRecon Attack Surface Summary ===\n\n")
#             for cat, items in self.surface.items():
#                 f.write(f"[{cat.upper()}] ({len(items)})\n")
#                 for d in sorted(items):
#                     f.write(f"  - {d}\n")
#                 f.write("\n")
#
#     # --------------------------------------------------------------------------------------------------
#     def run(self):
#         print(Y + "[*] Loading context..." + W)
#         self.load_context()
#
#         print(Y + "[*] Building attack surface..." + W)
#         self.build_surface()
#
#         self.save_outputs()
#
#         print(G + "[+] Attack surface built successfully!" + W)
#         print(G + f"[+] Categories: {len(self.surface)}" + W)
#         print(G + f"[+] Priority targets: {len(self.priority_targets)}" + W)
#         print(G + f"[+] Output in: {self.output_dir}" + W)
