# --------------------------------------------------------------------------------------------------
# TugaRecon – Context Engine (Refactored)
# File: modules/Brute_force/tuga_context.py
#
# Este módulo é responsável por construir CONTEXTO operacional a partir de:
#   1. Subdomínios descobertos (bruteforce)
#   2. Dados de serviços identificados (HTTP probe / enumeração)
#
# O objetivo não é atacar.
# O objetivo é modelar:
#   - Superfície exposta
#   - Infraestrutura partilhada
#   - Alvos de maior valor
#
# Isto é uma camada de "inteligência estrutural".
# --------------------------------------------------------------------------------------------------

import os
import json
import socket
from collections import defaultdict
from utils.tuga_colors import G, Y, R, W


# --------------------------------------------------------------------------------------------------
class TugaContext:
    """
    TugaContext é um motor de agregação contextual.

    Ele:
        - Liga subdomínios a IPs (resolução DNS)
        - Associa serviços detectados a hosts
        - Calcula risco heurístico básico
        - Constrói mapa de infraestrutura (IP -> domínios)
        - Identifica alvos de alto valor

    NÃO faz:
        - Exploração
        - Scanning ativo
        - Inferência de attack paths (isso é outro módulo)
    """

    # --------------------------------------------------------------------------------------------------
    def __init__(self, bruteforce_file, services_file, output_dir):
        """
        Inicializa o contexto com:
            bruteforce_file → ficheiro com subdomínios encontrados
            services_file   → JSON com resultados de enumeração de serviços
            output_dir      → diretório onde serão guardados os outputs

        Estruturas internas:
            subdomains      → { domain: [ips] }
            services        → { host: service_json }
            context         → { domain: enriched_entry }
            infrastructure  → { ip: [domains] }
            high_value_targets → lista de domínios com score elevado
        """

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
    def resolve_ip(self, domain):
        """
        Resolve um domínio para IPs usando getaddrinfo.

        Retorna:
            Lista de IPs únicos.

        Caso falhe (DNS error, timeout, etc):
            Retorna lista vazia.

        Isto permite:
            - Detectar infraestrutura partilhada
            - Mapear múltiplos domínios para o mesmo IP
        """
        try:
            return list(set([ip[4][0] for ip in socket.getaddrinfo(domain, None)]))
        except:
            return []

    # --------------------------------------------------------------------------------------------------
    def load_subdomains(self):
        """
        Lê o ficheiro de bruteforce e:
            - Extrai cada domínio
            - Resolve IPs dinamicamente
            - Preenche self.subdomains

        Resultado:
            self.subdomains = {
                "api.example.com": ["1.2.3.4"],
                ...
            }
        """

        if not os.path.isfile(self.bruteforce_file):
            print(Y + f"[*] Subdomains file not found: {self.bruteforce_file}, skipping..." + W)
            return

        with open(self.bruteforce_file) as f:
            for line in f:
                domain = line.strip().split()[0]
                if not domain:
                    continue

                ips = self.resolve_ip(domain)
                self.subdomains[domain] = ips

        print(G + f"[+] Loaded {len(self.subdomains)} subdomains" + W)

    # --------------------------------------------------------------------------------------------------
    def load_services(self):
        """
        Carrega dados de serviços previamente recolhidos.

        Espera um JSON no formato:
            [
                {
                    "host": "api.example.com",
                    "status": 200,
                    "title": "Login Panel",
                    ...
                }
            ]

        Resultado:
            self.services = {
                "api.example.com": {...}
            }
        """

        if not os.path.isfile(self.services_file):
            print(R + f"[!] Services file not found: {self.services_file}" + W)
            return

        with open(self.services_file) as f:
            data = json.load(f)
            for entry in data:
                host = entry.get("host")
                if host:
                    self.services[host] = entry

        print(G + f"[+] Loaded {len(self.services)} services" + W)

    # --------------------------------------------------------------------------------------------------
    def detect_risk(self, domain, service):
        """
        Aplica heurísticas simples para atribuir um risk_score.

        Baseia-se em:
            - Palavras-chave no subdomínio
            - Status HTTP
            - Título da página

        Retorna:
            score (int)
            flags (lista explicativa)

        Este score NÃO é impacto técnico profundo.
        É apenas um indicador de interesse ofensivo.
        """

        score = 0
        flags = []

        risky_keywords = [
            "admin", "dev", "test", "internal", "vpn", "mail", "api",
            "jira", "git", "db", "grafana", "jenkins", "panel"
        ]

        # Análise lexical do domínio
        for k in risky_keywords:
            if k in domain.lower():
                score += 2
                flags.append(f"keyword:{k}")

        # Análise baseada no serviço detectado
        if service:
            status = service.get("status", 0)
            title = (service.get("title") or "").lower()

            if status in [200, 302]:
                score += 2

            if "login" in title:
                score += 3
                flags.append("login_panel")

            if "grafana" in title:
                score += 5
                flags.append("grafana_panel")

            if "jenkins" in title:
                score += 5
                flags.append("ci_panel")

        return score, flags

    # --------------------------------------------------------------------------------------------------
    def build_context(self):
        """
        Constrói o contexto consolidado:

        Para cada domínio:
            - Associa serviço
            - Calcula risco
            - Guarda estrutura enriquecida
            - Atualiza mapa de infraestrutura
            - Marca high_value_targets

        Resultado final:
            self.context
            self.infrastructure
            self.high_value_targets
        """

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

            # Infraestrutura partilhada
            for ip in ips:
                self.infrastructure[ip].append(domain)

            # Threshold simples de alto valor
            if score >= 5:
                self.high_value_targets.append(domain)

        print(G + f"[+] Context entries: {len(self.context)}" + W)

    # --------------------------------------------------------------------------------------------------
    def save_outputs(self):
        """
        Persiste resultados no disco:

            context.json
                → dados completos por domínio

            infrastructure_map.json
                → IP → domínios

            high_value_targets.txt
                → lista simples para uso rápido
        """

        with open(os.path.join(self.output_dir, "context.json"), "w") as f:
            json.dump(self.context, f, indent=2)

        with open(os.path.join(self.output_dir, "infrastructure_map.json"), "w") as f:
            json.dump(self.infrastructure, f, indent=2)

        with open(os.path.join(self.output_dir, "high_value_targets.txt"), "w") as f:
            for d in sorted(set(self.high_value_targets)):
                f.write(d + "\n")

    # --------------------------------------------------------------------------------------------------
    def run(self):
        """

        Ordem:
            1. Carrega subdomínios
            2. Carrega serviços
            3. Constrói contexto
            4. Guarda resultados


        """

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
