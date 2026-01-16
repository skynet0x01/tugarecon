# --------------------------------------------------------------------------------------------------
# TugaRecon
# Author: Skynet0x01 2020-2026
# GitHub: https://github.com/skynet0x01/tugarecon
# License: GNU GPLv3
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.
# --------------------------------------------------------------------------------------------------
import os
import dns.resolver
import time
import datetime
import sys
import signal
import queue
from uuid import uuid4

from multiprocessing import Queue, Process, freeze_support, Value, Lock
from utils.tuga_colors import G, Y, R, W


# ----------------------------------------------------------------------------------------------------------
class TugaBruteForce:
    SPINNER = ['|', '/', '-', '\\']

    def __init__(self, options: dict):
        freeze_support()

        self.options = options
        self.target = options.get("target")
        self.workers = options.get("threads", 100)

        self.first_wordlist = "wordlist/first_names.txt"
        self.second_wordlist = "wordlist/next_names.txt"

        self.start = time.time()

        self.first_sub_names = Queue()
        self.subdomains_count = Value('i', 0)

        self.print_lock = Lock()
        self.file_lock = Lock()

        # ---- SEMANTIC INIT ----
        self.semantic_hints = options.get("semantic_hints", [])

        self.load_first_sub_names()
        self.second_sub_names = self.load_second_sub_names()

        self.dns_servers = self.load_dns_servers("dnslist/dns_servers.txt")
        self.online_dns_servers = self.get_online_dns_servers()

        self.dns_index = Value('i', 0)
        self.dns_index_lock = Lock()

        self.date = str(datetime.datetime.now().date())
        pwd = os.getcwd()

        self.folder = os.path.join(pwd, "results", self.target, self.date)

        os.makedirs(self.folder, exist_ok=True)
        self.outfile_path = os.path.join(self.folder, "tuga_bruteforce.txt")

        self.spinner_index = 0

        self.resolvers = []
        for server in self.online_dns_servers:
            r = dns.resolver.Resolver(configure=False)
            r.nameservers = [server]
            r.lifetime = 1.6
            self.resolvers.append(r)

        self.wildcard_ips = self.detect_wildcard() or set()

    # ----------------------------------------------------------------------------------------------------------

    def load_first_sub_names(self):
        seen = set()

        for h in getattr(self, "semantic_hints", []):
            if h not in seen:
                self.first_sub_names.put(h)
                seen.add(h)

        with open(self.first_wordlist, 'r') as file:
            for linha in file:
                w = linha.strip()
                if w and w not in seen:
                    self.first_sub_names.put(w)
                    seen.add(w)

    def load_second_sub_names(self):
        if not os.path.exists(self.second_wordlist):
            return []
        with open(self.second_wordlist) as file:
            return [l.strip() for l in file if l.strip()]

    def load_dns_servers(self, filepath):
        servers = []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    servers.append(line)
        return servers

    # ----------------------------------------------------------------------------------------------------------

    def get_online_dns_servers(self, test_domain="google.com"):
        online = []
        for server in self.dns_servers:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [server]
            resolver.lifetime = 1.5
            try:
                resolver.resolve(test_domain, "A")
                online.append(server)
            except Exception:
                continue
        return online if online else self.dns_servers

    # ----------------------------------------------------------------------------------------------------------

    def resolve_fast(self, domain):
        dns_count = len(self.resolvers)
        last_error = None

        for _ in range(dns_count):
            with self.dns_index_lock:
                idx = self.dns_index.value
                resolver = self.resolvers[idx]
                self.dns_index.value = (idx + 1) % dns_count

            try:
                answer = resolver.resolve(domain, "A")
                ips = [rdata.to_text() for rdata in answer]

                if self.wildcard_ips and set(ips) == self.wildcard_ips:
                    return None

                return ips

            except Exception as e:
                last_error = e
                continue

        if last_error:
            self.log_error(domain, str(last_error))

        return None

    # ----------------------------------------------------------------------------------------------------------

    def detect_wildcard(self):
        test = f"{uuid4().hex}.{self.target}"
        ips = self.resolve_fast(test)
        return set(ips) if ips else set()

    # ----------------------------------------------------------------------------------------------------------

    def print_testing(self, domain):
        with self.print_lock:
            spinner_char = self.SPINNER[self.spinner_index % len(self.SPINNER)]
            self.spinner_index += 1
            msg = f"Testing {spinner_char} : {domain}"
            sys.stdout.write('\r' + msg.ljust(90))
            sys.stdout.flush()

    def print_valid(self, count, domain, ips):
        with self.print_lock:
            sys.stdout.write('\r' + ' ' * 120 + '\r')
            domain_col_width = 60
            ips_display = ", ".join(ips) if ips else "-"
            print(f"{G}[*] {count}:{W}   {domain.ljust(domain_col_width)} {ips_display}")
            sys.stdout.flush()

    # ----------------------------------------------------------------------------------------------------------

    def log_error(self, domain, message):
        log_file = os.path.join(self.folder, "dns_errors.log")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.print_lock:
            with open(log_file, 'a') as f:
                f.write(f"[{timestamp}] DNS Error for {domain}: {message}\n")

    # ----------------------------------------------------------------------------------------------------------

    def handle_valid_subdomain(self, domain, ips):
        with self.subdomains_count.get_lock():
            self.subdomains_count.value += 1
            count = self.subdomains_count.value

        self.print_valid(count, domain, ips)

        with self.file_lock:
            with open(self.outfile_path, 'a') as f:
                f.write(f"{domain}\t{','.join(ips)}\n")

    # ----------------------------------------------------------------------------------------------------------

    def scan_subdomains(self):
        try:
            signal.signal(signal.SIGINT, signal.SIG_IGN)
        except Exception:
            pass

        try:
            while True:
                try:
                    first = self.first_sub_names.get(timeout=0.2)
                except queue.Empty:
                    break

                sub1 = f"{first}.{self.target}"
                self.print_testing(sub1)

                ips = self.resolve_fast(sub1)
                if ips:
                    self.handle_valid_subdomain(sub1, ips)

                    for second in self.second_sub_names:
                        sub2 = f"{second}.{sub1}"
                        self.print_testing(sub2)
                        ips2 = self.resolve_fast(sub2)
                        if ips2:
                            self.handle_valid_subdomain(sub2, ips2)

        except Exception as e:
            self.log_error("scan_subdomains", str(e))

    # ----------------------------------------------------------------------------------------------------------

    def start_process(self):
        processes = []

        try:
            for i in range(self.workers):
                p = Process(target=self.scan_subdomains, name=f"worker-{i}")
                p.start()
                processes.append(p)

            while any(p.is_alive() for p in processes):
                for p in processes:
                    p.join(timeout=0.5)

        except KeyboardInterrupt:
            print(R + "\n[!] User forced interrupt! Terminating workers..." + W)
            for p in processes:
                if p.is_alive():
                    p.terminate()
            sys.exit(1)

    # ----------------------------------------------------------------------------------------------------------

    def run(self):
        try:
            self.start_process()
        finally:
            with self.print_lock:
                sys.stdout.write('\r' + ' ' * 120 + '\r')
                sys.stdout.flush()

            print(Y + f"\n[*] Total Subdomains Found: {self.subdomains_count.value}" + W)
            print(Y + f"[**] TugaRecon finished in {time.time() - self.start:.2f}s" + W)
            print(G + f"[+] Results saved in: {self.folder}" + W)
            sys.exit(0)
