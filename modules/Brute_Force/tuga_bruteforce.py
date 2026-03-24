# ----------------------------------------------------------------------------------------------------------
# TugaRecon – DNS Bruteforce Engine (v3.1 ULTRA FAST + OUTPUT IMEDIATO + CORES)
# ----------------------------------------------------------------------------------------------------------
# OBJETIVO:
#   - Mostrar resultados IMEDIATAMENTE (sem delay inicial)
#   - Manter alta performance
#   - Adicionar CORES no output
#   - Código explicado para LEIGOS
# ----------------------------------------------------------------------------------------------------------

# ==========================================
# IMPORTS (Explicação simples)
# ==========================================

import dns.resolver              # Faz pedidos DNS (descobre IPs de domínios)
import threading                 # Permite várias tarefas ao mesmo tempo (threads)
import time                      # Medir tempo de execução
import os                        # Trabalhar com ficheiros e pastas
import random                    # Randomizar DNS (evitar bloqueios)
from uuid import uuid4           # Criar domínios falsos (detetar wildcard)
from concurrent.futures import ThreadPoolExecutor  # Motor de paralelismo

from utils.tuga_colors import G, Y, R, W  # Cores para output

# ==========================================
# CLASSE PRINCIPAL
# ==========================================

class TugaBruteForce:

    def __init__(self, options: dict):

        # -------------------------
        # CONFIG
        # -------------------------

        self.target = options.get("target")
        self.threads = options.get("threads", 100)

        self.first_wordlist = "wordlist/first_names.txt"
        self.second_wordlist = "wordlist/next_names.txt"

        self.start = time.time()

        # -------------------------
        # CACHE GLOBAL (EVITA REPETIÇÕES)
        # -------------------------

        self.cache = {}
        self.cache_lock = threading.Lock()

        # -------------------------
        # CONTADOR GLOBAL
        # -------------------------

        self.count = 0
        self.count_lock = threading.Lock()

        # -------------------------
        # LOAD WORDLISTS
        # -------------------------

        self.first_subs = self.load_list(self.first_wordlist)
        self.second_subs = self.load_list(self.second_wordlist)

        # -------------------------
        # DNS
        # -------------------------

        self.dns_servers = self.load_dns("dnslist/dns_servers.txt")
        self.resolvers = self.create_resolvers()

        # -------------------------
        # WILDCARD
        # -------------------------

        self.wildcard_ips = self.detect_wildcard()

        # -------------------------
        # OUTPUT FILE
        # -------------------------

        self.outfile = "results.txt"

    # ==========================================
    # LOAD LISTA
    # ==========================================

    def load_list(self, path):
        if not os.path.exists(path):
            return []

        with open(path) as f:
            return [l.strip() for l in f if l.strip()]

    # ==========================================
    # LOAD DNS
    # ==========================================

    def load_dns(self, path):
        with open(path) as f:
            return [l.strip() for l in f if l.strip() and not l.startswith("#")]

    # ==========================================
    # CRIAR RESOLVERS
    # ==========================================

    def create_resolvers(self):
        resolvers = []

        # RANDOMIZA LISTA (IMPORTANTE PARA EVASÃO)
        random.shuffle(self.dns_servers)

        for server in self.dns_servers:
            r = dns.resolver.Resolver(configure=False)
            r.nameservers = [server]

            # TIMEOUT AGRESSIVO = MAIS RÁPIDO
            r.timeout = 0.8
            r.lifetime = 0.8

            resolvers.append(r)

        return resolvers

    # ==========================================
    # RESOLVER DOMÍNIO
    # ==========================================

    def resolve(self, domain):

        # CACHE
        with self.cache_lock:
            if domain in self.cache:
                return self.cache[domain]

        # RANDOMIZA RESOLVERS (MUITO IMPORTANTE)
        resolvers = self.resolvers.copy()
        random.shuffle(resolvers)

        nx = 0

        for i, resolver in enumerate(resolvers):

            # NÃO TESTAR TODOS (GANHO DE VELOCIDADE)
            if i >= 3:
                break

            try:
                answer = resolver.resolve(domain, "A")
                ips = [r.to_text() for r in answer]

                # EVITAR WILDCARD
                if self.wildcard_ips and set(ips) == self.wildcard_ips:
                    return None

                with self.cache_lock:
                    self.cache[domain] = ips

                return ips

            except dns.resolver.NXDOMAIN:
                nx += 1
                if nx >= 2:
                    with self.cache_lock:
                        self.cache[domain] = None
                    return None

            except Exception:
                continue

        with self.cache_lock:
            self.cache[domain] = None

        return None

    # ==========================================
    # DETETAR WILDCARD
    # ==========================================

    def detect_wildcard(self):
        results = []

        for _ in range(3):
            test = f"{uuid4().hex}.{self.target}"

            for resolver in self.resolvers:
                try:
                    answer = resolver.resolve(test, "A")
                    ips = {r.to_text() for r in answer}
                    results.append(ips)
                    break
                except:
                    continue

        if len(results) >= 2 and all(r == results[0] for r in results):
            print(Y + "[!] Wildcard detectado" + W)
            return results[0]

        return set()

    # ==========================================
    # OUTPUT (IMEDIATO)
    # ==========================================

    def save(self, domain, ips):

        with self.count_lock:
            self.count += 1
            c = self.count

        # PRINT IMEDIATO (SEM LOCK = MAIS RÁPIDO)
        print(f"{G}[*] {c}:{W} {domain.ljust(50)} {', '.join(ips)}")

        # FILE LOCK
        with open(self.outfile, "a") as f:
            f.write(f"{domain}\t{','.join(ips)}\n")

    # ==========================================
    # SCAN PRIMEIRO NÍVEL
    # ==========================================

    def scan_first(self, sub):

        domain = f"{sub}.{self.target}"

        ips = self.resolve(domain)

        if ips:
            self.save(domain, ips)

        # IMPORTANTE: segundo nível NÃO BLOQUEIA
        for s in self.second_subs:
            self.executor.submit(self.scan_second, s, domain)

    # ==========================================
    # SCAN SEGUNDO NÍVEL
    # ==========================================

    def scan_second(self, sub, parent):

        domain = f"{sub}.{parent}"

        ips = self.resolve(domain)

        if ips:
            self.save(domain, ips)

    # ==========================================
    # RUN
    # ==========================================

    def run(self):

        print(G + "[+] Scan ultra-rápido iniciado..." + W)

        # UM ÚNICO EXECUTOR GLOBAL (SEM BLOQUEIOS)
        self.executor = ThreadPoolExecutor(max_workers=self.threads)

        # DISPARA TODAS AS TASKS IMEDIATAMENTE
        for sub in self.first_subs:
            self.executor.submit(self.scan_first, sub)

        # ESPERA TERMINAR
        self.executor.shutdown(wait=True)

        print(Y + f"\n[*] Total encontrado: {self.count}" + W)
        print(Y + f"[**] Tempo: {time.time() - self.start:.2f}s" + W)

# ----------------------------------------------------------------------------------------------------------
# USO
# ----------------------------------------------------------------------------------------------------------

# options = {
#     "target": "tesla.com",
#     "threads": 150
# }

# scanner = TugaBruteForce(options)
# scanner.run()



# # ----------------------------------------------------------------------------------------------------------
# # TugaRecon – DNS Bruteforce Engine
# #
# # Este módulo é responsável por:
# #   - Gerar combinações de subdomínios
# #   - Resolver DNS em paralelo (multiprocessing)
# #   - Detectar wildcard DNS
# #   - Guardar resultados válidos
# #
# # NÃO faz:
# #   - Análise semântica
# #   - Avaliação de impacto
# #   - HTTP probing
# #
# # Ele é a camada de descoberta bruta.
# # ----------------------------------------------------------------------------------------------------------
#
# import datetime
# import sys
# import signal
# import queue
# import os
# import time
# import dns.resolver
#
# from uuid import uuid4
# from multiprocessing import Queue, Process, freeze_support, Value, Lock
# from utils.tuga_colors import G, Y, R, W
#
#
# class TugaBruteForce:
#     """
#     Motor de brute force DNS multiprocessado.
#
#     Estratégia:
#         - Fila compartilhada com primeiros labels
#         - Expansão opcional com segundo nível
#         - Round-robin entre resolvers DNS
#         - Cache local para evitar repetição
#         - Detecção automática de wildcard DNS
#
#     Arquiteturalmente:
#         Recon Layer → Descoberta de superfície
#     """
#
#     SPINNER = ['|', '/', '-', '\\']
#
#     # ----------------------------------------------------------------------------------------------------------
#     def __init__(self, options: dict):
#         """
#         Inicializa motor de bruteforce.
#
#         options:
#             target          → domínio base
#             threads         → número de processos
#             semantic_hints  → palavras derivadas de OSINT/contexto
#
#         Usa multiprocessing:
#             Queue → tarefas
#             Value → contador compartilhado
#             Lock  → sincronização
#         """
#
#         freeze_support()  # necessário para compatibilidade Windows
#
#         self.options = options
#         self.target = options.get("target")
#         self.workers = options.get("threads", 100)
#
#         self.first_wordlist = "wordlist/first_names.txt"
#         self.second_wordlist = "wordlist/next_names.txt"
#
#         self.start = time.time()
#
#         self.first_sub_names = Queue()
#         self.subdomains_count = Value('i', 0)
#
#         self.print_lock = Lock()
#         self.file_lock = Lock()
#
#         # Palavras derivadas de OSINT / IA
#         self.semantic_hints = options.get("semantic_hints", [])
#
#         self.load_first_sub_names()
#         self.second_sub_names = self.load_second_sub_names()
#
#         # DNS infrastructure
#         self.dns_servers = self.load_dns_servers("dnslist/dns_servers.txt")
#         self.online_dns_servers = self.get_online_dns_servers()
#
#         self.dns_index = Value('i', 0)
#         self.dns_index_lock = Lock()
#
#         self.date = str(datetime.datetime.now().date())
#         pwd = os.getcwd()
#         self.folder = os.path.join(pwd, "results", self.target, self.date)
#         os.makedirs(self.folder, exist_ok=True)
#         self.outfile_path = os.path.join(self.folder, "tuga_bruteforce.txt")
#
#         self.spinner_index = 0
#
#         # Resolver pool
#         self.resolvers = []
#         for server in self.online_dns_servers:
#             r = dns.resolver.Resolver(configure=False)
#             r.nameservers = [server]
#             r.lifetime = 1.6
#             r.timeout = 1.6
#             self.resolvers.append(r)
#
#         # Cache DNS local
#         self.local_dns_cache = {}
#
#         # Detecta wildcard DNS
#         self.wildcard_ips = self.detect_wildcard() or set()
#
#     # ----------------------------------------------------------------------------------------------------------
#     def load_first_sub_names(self):
#         """
#         Carrega:
#             - semantic hints primeiro
#             - depois wordlist principal
#
#         Usa set() para evitar duplicados.
#         Preenche Queue compartilhada.
#         """
#
#         seen = set()
#
#         for h in getattr(self, "semantic_hints", []):
#             if h not in seen:
#                 self.first_sub_names.put(h)
#                 seen.add(h)
#
#         with open(self.first_wordlist, 'r') as file:
#             for linha in file:
#                 w = linha.strip()
#                 if w and w not in seen:
#                     self.first_sub_names.put(w)
#                     seen.add(w)
#
#     # ----------------------------------------------------------------------------------------------------------
#     def load_second_sub_names(self):
#         """
#         Carrega wordlist secundária (sub-subdomínios).
#         Pode não existir.
#         """
#         if not os.path.exists(self.second_wordlist):
#             return []
#
#         with open(self.second_wordlist) as file:
#             return [l.strip() for l in file if l.strip()]
#
#     # ----------------------------------------------------------------------------------------------------------
#     def load_dns_servers(self, filepath):
#         """
#         Lê lista de DNS resolvers.
#         Ignora comentários.
#         """
#         servers = []
#         with open(filepath, 'r') as f:
#             for line in f:
#                 line = line.strip()
#                 if line and not line.startswith("#"):
#                     servers.append(line)
#         return servers
#
#     # ----------------------------------------------------------------------------------------------------------
#     def get_online_dns_servers(self, test_domain="google.com"):
#         """
#         Testa cada DNS server tentando resolver domínio conhecido.
#
#         Retorna apenas os que respondem.
#         Fallback → lista original se todos falharem.
#         """
#         online = []
#
#         for server in self.dns_servers:
#             resolver = dns.resolver.Resolver()
#             resolver.nameservers = [server]
#             resolver.lifetime = 1.5
#
#             try:
#                 resolver.resolve(test_domain, "A")
#                 online.append(server)
#             except Exception:
#                 continue
#
#         return online if online else self.dns_servers
#
#     # ----------------------------------------------------------------------------------------------------------
#     def resolve_fast(self, domain):
#         """
#         Resolve domínio usando:
#             - Round-robin entre resolvers
#             - Cache local
#             - Detecção de wildcard
#
#         Retorna:
#             Lista de IPs ou None
#         """
#
#         if domain in self.local_dns_cache:
#             return self.local_dns_cache[domain]
#
#         dns_count = len(self.resolvers)
#         last_error = None
#
#         for _ in range(dns_count):
#             with self.dns_index_lock:
#                 idx = self.dns_index.value
#                 resolver = self.resolvers[idx]
#                 self.dns_index.value = (idx + 1) % dns_count
#
#             try:
#                 answer = resolver.resolve(domain, "A", lifetime=1.8)
#                 ips = [rdata.to_text() for rdata in answer]
#
#                 # Filtra wildcard DNS
#                 if self.wildcard_ips and set(ips) == self.wildcard_ips:
#                     self.local_dns_cache[domain] = None
#                     return None
#
#                 self.local_dns_cache[domain] = ips
#                 return ips
#
#             except dns.resolver.Timeout:
#                 continue
#
#             except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
#                 self.local_dns_cache[domain] = None
#                 return None
#
#             except Exception as e:
#                 last_error = e
#                 continue
#
#         if last_error:
#             self.log_error(domain, str(last_error))
#
#         self.local_dns_cache[domain] = None
#         return None
#
#     # ----------------------------------------------------------------------------------------------------------
#     def detect_wildcard(self):
#         """
#         Detecta wildcard DNS criando subdomínio aleatório.
#
#         Se resolver para IP fixo:
#             domínio usa wildcard
#         """
#         test = f"{uuid4().hex}.{self.target}"
#         ips = self.resolve_fast(test)
#         return set(ips) if ips else set()
#
#     # ----------------------------------------------------------------------------------------------------------
#     def handle_valid_subdomain(self, domain, ips):
#         """
#         Incrementa contador compartilhado.
#         Guarda resultado no ficheiro.
#         Output thread-safe.
#         """
#
#         with self.subdomains_count.get_lock():
#             self.subdomains_count.value += 1
#             count = self.subdomains_count.value
#
#         with self.file_lock:
#             with open(self.outfile_path, 'a') as f:
#                 f.write(f"{domain}\t{','.join(ips)}\n")
#
#         print(f"{G}[*] {count}:{W}   {domain.ljust(60)} {', '.join(ips)}")
#
#     # ----------------------------------------------------------------------------------------------------------
#     def scan_subdomains(self):
#         """
#         Worker principal.
#
#         Loop:
#             - Retira label da queue
#             - Resolve domínio
#             - Se válido:
#                 - guarda
#                 - tenta subnível (second wordlist)
#         """
#
#         try:
#             while True:
#                 try:
#                     first = self.first_sub_names.get(timeout=0.2)
#                 except queue.Empty:
#                     break
#
#                 sub1 = f"{first}.{self.target}"
#                 ips = self.resolve_fast(sub1)
#
#                 if ips:
#                     self.handle_valid_subdomain(sub1, ips)
#
#                     for second in self.second_sub_names:
#                         sub2 = f"{second}.{sub1}"
#                         ips2 = self.resolve_fast(sub2)
#                         if ips2:
#                             self.handle_valid_subdomain(sub2, ips2)
#
#         except Exception as e:
#             self.log_error("scan_subdomains", str(e))
#
#     # ----------------------------------------------------------------------------------------------------------
#     def start_process(self):
#         """
#         Cria N processos workers.
#         Aguarda conclusão.
#         Trata Ctrl+C.
#         """
#
#         processes = []
#
#         try:
#             for i in range(self.workers):
#                 p = Process(target=self.scan_subdomains, name=f"worker-{i}")
#                 p.start()
#                 processes.append(p)
#
#             for p in processes:
#                 p.join()
#
#         except KeyboardInterrupt:
#             print(R + "\n[!] User forced interrupt! Terminating workers..." + W)
#             for p in processes:
#                 if p.is_alive():
#                     p.terminate()
#             sys.exit(1)
#
#     # ----------------------------------------------------------------------------------------------------------
#     def run(self):
#         """
#         Entry point do bruteforce.
#
#         Executa workers.
#         Limpa output visual.
#         Mostra estatísticas finais.
#         """
#
#         try:
#             self.start_process()
#         finally:
#             print(Y + f"\n[*] Total Subdomains Found: {self.subdomains_count.value}" + W)
#             print(Y + f"[**] TugaRecon finished in {time.time() - self.start:.2f}s" + W)
#             print(G + f"[+] Results saved in: {self.folder}" + W)
#             sys.exit(0)
