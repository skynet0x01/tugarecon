# --------------------------------------------------------------------------------------------------
# TugaRecon – Context Engine
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

import os
import json
import socket
import time
from collections import defaultdict
from utils.tuga_colors import G, Y, R, W

# --------------------------------------------------------------------------------------------------
class TugaContext:

    def __init__(self, bruteforce_file, services_file, output_dir):
        self.bruteforce_file = bruteforce_file
        self.services_file = services_file
        self.output_dir = output_dir

        os.makedirs(self.output_dir, exist_ok=True)

        self.subdomains = {}
        self.services = {}
        self.context = {}
        self.infrastructure = defaultdict(list)
        self.high_value_targets = []

    # --------------------------------------------------------------------------------------------------
    def load_subdomains(self):
        if not os.path.isfile(self.bruteforce_file):
            print(Y + f"[*] Subdomains file not found: {self.bruteforce_file}, skipping..." + W)
            return  # não faz nada se o ficheiro não existir

        with open(self.bruteforce_file) as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) >= 2:
                    domain = parts[0]
                    ips = parts[1].split(",")
                    self.subdomains[domain] = ips

    # --------------------------------------------------------------------------------------------------
    def load_services(self):
        with open(self.services_file) as f:
            data = json.load(f)
            for entry in data:
                self.services[entry["host"]] = entry

    # --------------------------------------------------------------------------------------------------
    def detect_risk(self, domain, service):
        score = 0
        flags = []

        risky_keywords = ["admin", "dev", "test", "internal", "vpn", "mail", "api", "jira", "git", "db"]

        for k in risky_keywords:
            if k in domain.lower():
                score += 2
                flags.append(f"keyword:{k}")

        if service:
            if service.get("status") in [200, 302]:
                score += 2
            if "login" in (service.get("title") or "").lower():
                score += 3
                flags.append("login_panel")

            if "grafana" in (service.get("title") or "").lower():
                score += 5
                flags.append("grafana_panel")

        return score, flags

    # --------------------------------------------------------------------------------------------------
    def build_context(self):
        for domain, ips in self.subdomains.items():
            service = self.services.get(domain)
            score, flags = self.detect_risk(domain, service)

            entry = {
                "domain": domain,
                "ips": ips,
                "service": service,
                "risk_score": score,
                "flags": flags
            }

            self.context[domain] = entry

            for ip in ips:
                self.infrastructure[ip].append(domain)

            if score >= 5:
                self.high_value_targets.append(domain)

    # --------------------------------------------------------------------------------------------------
    def save_outputs(self):
        with open(os.path.join(self.output_dir, "context.json"), "w") as f:
            json.dump(self.context, f, indent=2)

        with open(os.path.join(self.output_dir, "infrastructure_map.json"), "w") as f:
            json.dump(self.infrastructure, f, indent=2)

        with open(os.path.join(self.output_dir, "high_value_targets.txt"), "w") as f:
            for d in sorted(set(self.high_value_targets)):
                f.write(d + "\n")

    # --------------------------------------------------------------------------------------------------
    def run(self):
        print(Y + "[*] Loading subdomains..." + W)
        self.load_subdomains()

        print(Y + "[*] Loading services..." + W)
        self.load_services()

        print(Y + "[*] Building context..." + W)
        self.build_context()

        self.save_outputs()

        print(G + "[+] Context built successfully!" + W)
        print(G + f"[+] High value targets: {len(self.high_value_targets)}" + W)
        print(G + f"[+] Output in: {self.output_dir}" + W)
