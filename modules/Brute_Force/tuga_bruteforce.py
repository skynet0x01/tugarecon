# ----------------------------------------------------------------------------------------------------------
# TugaRecon – DNS Bruteforce Engine (v2.0 Hardened+)
#
# Este módulo faz:
#   - Descoberta de subdomínios por brute force
#   - Usa múltiplos DNS para evitar bloqueios
#   - Deteta wildcard DNS (muito importante)
#   - Usa multiprocessing para ser rápido
#
# ----------------------------------------------------------------------------------------------------------

import datetime                  # Datas (para organizar resultados)
import sys                       # Permite terminar o programa
import queue                     # Filas (Queue)
import os                        # Sistema operativo (ficheiros, paths)
import time                      # Tempo (medir execução)
import random                    # Randomização (ESSENCIAL para DNS)
import dns.resolver              # Biblioteca para resolver DNS

from uuid import uuid4           # Gerar nomes aleatórios (wildcard test)
from multiprocessing import Queue, Process, freeze_support, Value, Lock
from utils.tuga_colors import G, Y, R, W  # Cores para output


class TugaBruteForce:

    # ------------------------------------------------------------------------------------------------------
    # INICIALIZAÇÃO
    # ------------------------------------------------------------------------------------------------------

    def __init__(self, options: dict):

        freeze_support()  # Necessário para multiprocessing em alguns sistemas

        self.options = options
        self.target = options.get("target")        # domínio alvo (ex: tesla.com)
        self.workers = options.get("threads", 50)  # número de processos

        # Caminhos das wordlists
        self.first_wordlist = "wordlist/first_names.txt"
        self.second_wordlist = "wordlist/next_names.txt"

        self.start = time.time()

        # Fila partilhada entre processos
        self.first_sub_names = Queue()

        # Contador global de resultados
        self.subdomains_count = Value('i', 0)

        # Locks para evitar conflitos
        self.file_lock = Lock()

        # Palavras vindas de OSINT (se existirem)
        self.semantic_hints = options.get("semantic_hints", [])

        # Carregar dados
        self.load_first_sub_names()
        self.second_sub_names = self.load_second_sub_names()

        # DNS
        self.dns_servers = self.load_dns_servers("dnslist/dns_servers.txt")
        self.online_dns_servers = self.get_online_dns_servers()

        # Pasta de resultados
        self.date = str(datetime.datetime.now().date())
        self.folder = os.path.join(os.getcwd(), "results", self.target, self.date)
        os.makedirs(self.folder, exist_ok=True)
        self.outfile_path = os.path.join(self.folder, "tuga_bruteforce.txt")

        # Cache local (cada processo terá a sua)
        self.local_dns_cache = {}

        # Criar resolvers e detetar wildcard
        self.resolvers = self.create_resolver_pool()
        self.wildcard_ips = self.detect_wildcard()

    # ------------------------------------------------------------------------------------------------------
    # WORDLISTS
    # ------------------------------------------------------------------------------------------------------

    def load_first_sub_names(self):
        """
        Carrega:
            - palavras OSINT
            - wordlist principal

        Evita duplicados
        """
        seen = set()

        # 1. Palavras vindas de OSINT
        for hint in self.semantic_hints:
            if hint not in seen:
                self.first_sub_names.put(hint)
                seen.add(hint)

        # 2. Wordlist principal
        if not os.path.exists(self.first_wordlist):
            return

        with open(self.first_wordlist, 'r') as f:
            for line in f:
                word = line.strip()
                if word and word not in seen:
                    self.first_sub_names.put(word)
                    seen.add(word)

    # ------------------------------------------------------------------------------------------------------

    def load_second_sub_names(self):
        """
        Segunda wordlist (ex: dev.api.site.com)
        """
        if not os.path.exists(self.second_wordlist):
            return []

        with open(self.second_wordlist) as f:
            return [l.strip() for l in f if l.strip()]

    # ------------------------------------------------------------------------------------------------------
    # DNS
    # ------------------------------------------------------------------------------------------------------

    def load_dns_servers(self, filepath):
        """
        Lê ficheiro dns_servers.txt
        """
        servers = []

        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    servers.append(line)

        return servers

    # ------------------------------------------------------------------------------------------------------

    def get_online_dns_servers(self, test_domain="google.com"):
        """
        Testa quais DNS estão a funcionar
        """
        online = []

        for server in self.dns_servers:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [server]

            try:
                resolver.resolve(test_domain, "A")
                online.append(server)
            except Exception:
                continue

        return online if online else self.dns_servers

    # ------------------------------------------------------------------------------------------------------

    def create_resolver_pool(self):
        """
        Cria resolvers com ORDEM ALEATÓRIA
        """
        resolvers = []

        shuffled = random.sample(self.online_dns_servers, len(self.online_dns_servers))

        for server in shuffled:
            r = dns.resolver.Resolver(configure=False)
            r.nameservers = [server]
            r.lifetime = 0.8 # Default 1.5
            r.timeout = 0.8  # Default 1.5

            # Estatísticas básicas
            r.stats = {"timeouts": 0, "success": 0}

            resolvers.append(r)

        return resolvers

    # ------------------------------------------------------------------------------------------------------
    # RESOLUÇÃO DNS INTELIGENTE
    # ------------------------------------------------------------------------------------------------------

    def resolve_fast(self, domain, resolvers):
        """
        Resolve domínio usando múltiplos DNS
        """

        # Se já foi resolvido antes → usa cache
        if domain in self.local_dns_cache:
            return self.local_dns_cache[domain]

        # Randomiza ordem (muito importante)
        random_resolvers = random.sample(resolvers, len(resolvers))

        nx_hits = 0  # contador de NXDOMAIN

        for resolver in random_resolvers:

            try:
                answer = resolver.resolve(domain, "A")
                ips = [r.to_text() for r in answer]

                resolver.stats["success"] += 1

                # Evita wildcard
                if self.wildcard_ips and set(ips) == self.wildcard_ips:
                    return None

                self.local_dns_cache[domain] = ips
                return ips

            except dns.resolver.Timeout:
                resolver.stats["timeouts"] += 1
                continue

            except dns.resolver.NXDOMAIN:
                nx_hits += 1

                # Só aceitar NXDOMAIN após 2 confirmações
                if nx_hits >= 2:
                    self.local_dns_cache[domain] = None
                    return None

                continue

            except Exception:
                continue

        self.local_dns_cache[domain] = None
        return None

    # ------------------------------------------------------------------------------------------------------
    # WILDCARD DETECTION
    # ------------------------------------------------------------------------------------------------------

    def detect_wildcard(self):
        """
        Testa se o domínio responde sempre com o mesmo IP (wildcard)
        """
        test_ips_sets = []

        for _ in range(3):
            test_domain = f"{uuid4().hex}.{self.target}"

            for resolver in self.resolvers:
                try:
                    answer = resolver.resolve(test_domain, "A")
                    ips = {r.to_text() for r in answer}
                    test_ips_sets.append(ips)
                    break
                except Exception:
                    continue

        if len(test_ips_sets) >= 2 and all(s == test_ips_sets[0] for s in test_ips_sets):
            return test_ips_sets[0]

        return set()

    # ------------------------------------------------------------------------------------------------------
    # OUTPUT
    # ------------------------------------------------------------------------------------------------------

    def handle_valid_subdomain(self, domain, ips):

        with self.subdomains_count.get_lock():
            self.subdomains_count.value += 1
            count = self.subdomains_count.value

        with self.file_lock:
            with open(self.outfile_path, 'a') as f:
                f.write(f"{domain}\t{','.join(ips)}\n")

        print(f"{G}[*] {count}:{W} {domain.ljust(50)} {', '.join(ips)}")

    # ------------------------------------------------------------------------------------------------------
    # WORKER
    # ------------------------------------------------------------------------------------------------------

    def scan_subdomains(self):

        # Cada processo cria o seu próprio pool
        resolvers = self.create_resolver_pool()

        try:
            while True:

                try:
                    first = self.first_sub_names.get(timeout=0.2)
                except queue.Empty:
                    break

                sub1 = f"{first}.{self.target}"

                ips = self.resolve_fast(sub1, resolvers)

                if ips:
                    self.handle_valid_subdomain(sub1, ips)

                    # Segundo nível
                    for second in self.second_sub_names:
                        sub2 = f"{second}.{sub1}"

                        ips2 = self.resolve_fast(sub2, resolvers)

                        if ips2:
                            self.handle_valid_subdomain(sub2, ips2)

        except Exception:
            pass

    # ------------------------------------------------------------------------------------------------------
    # PROCESSOS
    # ------------------------------------------------------------------------------------------------------

    def start_process(self):

        processes = []

        try:
            for _ in range(self.workers):
                p = Process(target=self.scan_subdomains)
                p.start()
                processes.append(p)

            for p in processes:
                p.join()

        except KeyboardInterrupt:
            print(R + "\n[!] Interrompido pelo utilizador" + W)
            for p in processes:
                if p.is_alive():
                    p.terminate()
            sys.exit(1)

    # ------------------------------------------------------------------------------------------------------
    # RUN
    # ------------------------------------------------------------------------------------------------------

    def run(self):

        try:
            self.start_process()
        finally:
            print(Y + f"\n[*] Total encontrado: {self.subdomains_count.value}" + W)
            print(Y + f"[**] Tempo: {time.time() - self.start:.2f}s" + W)
            print(G + f"[+] Resultados: {self.folder}" + W)
            sys.exit(0)