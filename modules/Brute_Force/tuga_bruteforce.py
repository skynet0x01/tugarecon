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
            r.lifetime = 1.5
            r.timeout = 1.5

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
