# --------------------------------------------------------------------------------------------------
# TugaRecon – Attack Surface Engine
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------

import os
import json
from collections import defaultdict
from utils.tuga_colors import G, Y, R, W

# --------------------------------------------------------------------------------------------------
class TugaAttackSurface:

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

        if "login_panel" in flags:
            return "auth_panels"
        if "grafana_panel" in flags:
            return "monitoring"
        if "api" in domain:
            return "api"
        if any(k in domain for k in ["mail", "smtp", "imap", "pop"]):
            return "mail"
        if any(k in domain for k in ["vpn", "remote"]):
            return "remote_access"
        if any(k in domain for k in ["dev", "test", "stage"]):
            return "non_prod"
        return "web"

    # --------------------------------------------------------------------------------------------------
    def build_surface(self):
        for domain, entry in self.context.items():
            category = self.classify(domain, entry)
            self.surface[category].append(domain)

            if entry.get("risk_score", 0) >= 5:
                self.priority_targets.append(domain)

    # --------------------------------------------------------------------------------------------------
    def save_outputs(self):
        with open(os.path.join(self.output_dir, "attack_surface.json"), "w") as f:
            json.dump(self.surface, f, indent=2)

        with open(os.path.join(self.output_dir, "priority_targets.txt"), "w") as f:
            for d in sorted(set(self.priority_targets)):
                f.write(d + "\n")

        with open(os.path.join(self.output_dir, "attack_surface_summary.txt"), "w") as f:
            f.write("=== TugaRecon Attack Surface Summary ===\n\n")
            for cat, items in self.surface.items():
                f.write(f"[{cat.upper()}] ({len(items)})\n")
                for d in sorted(items):
                    f.write(f"  - {d}\n")
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
