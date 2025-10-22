#!/usr/bin/python3
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01 2020-2025

# This file is part of TugaRecon, developed by skynet0x01 in 2020-2025.
#
# Copyright (C) 2025 skynet0x01
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Patent Restriction Notice:
# No patents may be claimed or enforced on this software or any derivative.
# Any patent claims will result in automatic termination of license rights under the GNU GPLv3.

# import go here
# ----------------------------------------------------------------------------------------------------------
import os
import dns.resolver
import time
import datetime
import sys
import signal

from multiprocessing import Queue, Process, freeze_support, Value, Lock
from utils.tuga_colors import G, Y, R, W
# ----------------------------------------------------------------------------------------------------------


class TugaBruteForce:
    SPINNER = ['|', '/', '-', '\\']  # Spinner animation characters for console feedback

    def __init__(self, options):
        freeze_support()  # Support for multiprocessing on Windows

        self.target = options.domain  # Target domain to brute force
        self.workers = options.threads  # Number of worker processes
        self.options = options
        self.first_wordlist = "wordlist/first_names.txt"  # First wordlist file path
        self.second_wordlist = "wordlist/next_names.txt"  # Second wordlist file path
        self.start = time.time()  # Start timestamp to measure duration

        self.first_sub_names = Queue()  # Queue for first-level subdomains
        self.subdomains_count = Value('i', 0)  # Shared counter for found subdomains
        self.print_lock = Lock()  # Lock to synchronize console output

        self.load_first_sub_names()  # Load first wordlist into queue
        self.second_sub_names = self.load_second_sub_names()  # Load second wordlist into list

        self.dns_servers = self.load_dns_servers("dnslist/dns_servers.txt")  # Load DNS servers list
        self.online_dns_servers = self.get_online_dns_servers()  # Filter only responsive DNS servers
        self.dns_index = Value('i', 0)  # Shared index to rotate DNS servers
        self.dns_index_lock = Lock()  # Lock to synchronize DNS server selection

        self.date = str(datetime.datetime.now().date())  # Current date for folder naming
        pwd = os.getcwd()
        self.folder = os.path.join(pwd, "results", self.target, self.date)  # Results folder path
        os.makedirs(self.folder, exist_ok=True)  # Create folder if not exists
        self.outfile_path = os.path.join(self.folder, "tuga_bruteforce.txt")  # Output file path

        self.spinner_index = 0  # Index to animate spinner in console

    # ----------------------------------------------------------------------------------------------------------

    def load_first_sub_names(self):
        # Load first wordlist and enqueue each subdomain candidate
        with open(self.first_wordlist, 'r') as file:
            for linha in file:
                self.first_sub_names.put(linha.strip())

    def load_second_sub_names(self):
        # Load second wordlist into a list for fast iteration
        with open(self.second_wordlist) as file:
            return [linha.strip() for linha in file]

    def load_dns_servers(self, filepath):
        # Load DNS server IPs from file, ignoring comments and blank lines
        servers = []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    servers.append(line)
        return servers

    # ----------------------------------------------------------------------------------------------------------

    def get_online_dns_servers(self, test_domain="google.com"):
        # Check which DNS servers are responsive by resolving a known domain
        online = []
        for server in self.dns_servers:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [server]
            resolver.lifetime = 1.5
            try:
                resolver.resolve(test_domain, "A")
                online.append(server)
            except:
                continue
        # Fallback to all servers if none respond
        return online if online else self.dns_servers


    def resolve_fast(self, domain):
        """
            Attempts to resolve the domain using the DNS servers in a round-robin fashion.
            Returns a list of IPs (strings) if it resolves successfully, or None
            if it cannot be resolved by any of the servers.
        """
        dns_count = len(self.online_dns_servers)

        for attempt in range(dns_count):
            with self.dns_index_lock:
                idx = self.dns_index.value
                dns_server = self.online_dns_servers[idx]
                self.dns_index.value = (idx + 1) % dns_count

            resolver = dns.resolver.Resolver()
            resolver.nameservers = [dns_server]
            resolver.lifetime = 1.6

            try:
                answer = resolver.resolve(domain, "A")
                # Extrai todos os IPs (como strings)
                ips = [rdata.to_text() for rdata in answer]
                return ips
            except Exception as e:
                self.log_error(domain, f"{e} (DNS {dns_server})")
                continue

        return None
# ----------------------------------------------------------------------------------------------------------


    def print_testing(self, domain):
        # Show rotating spinner with current testing domain on the same console line
        with self.print_lock:
            spinner_char = self.SPINNER[self.spinner_index % len(self.SPINNER)]
            self.spinner_index += 1
            msg = f"Testing {spinner_char} : {domain}"
            sys.stdout.write('\r' + msg.ljust(80))
            sys.stdout.flush()
# ----------------------------------------------------------------------------------------------------------


    def print_valid(self, count, domain, ips):
        """
        Clear spinner line and prints a formatted line with the domain and IPs aligned.
        The domain column has a fixed width to maintain spacing.
        """
        with self.print_lock:
            sys.stdout.write('\r' + ' ' * 120 + '\r')  # Clear line (maior largura)
            domain_col_width = 60  # ajusta se precisares de mais/menos espaço 45
            ips_display = ", ".join(ips) if ips else "-"
            # domain left-aligned em campo fixo, ips após esse campo
            print(f"{G}[*] {count}:{W}   {domain.ljust(domain_col_width)} {ips_display}")
            sys.stdout.flush()
# ----------------------------------------------------------------------------------------------------------


    def log_error(self, domain, message):
        # Append DNS errors to a dedicated log file (thread/process safe)
        log_file = os.path.join(self.folder, "dns_errors.log")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.print_lock:  # avoid concurrent writes
            with open(log_file, 'a') as f:
                f.write(f"[{timestamp}] DNS Error for {domain}: {message}\n")

    def scan_subdomains(self):
        """
        Worker process: ignora SIGINT (Ctrl+C) para evitar tracebacks nos filhos.
        Faz loop normal mas protege contra exceções e KeyboardInterrupt local.
        """
        # Ignorar SIGINT nos processos filhos — o pai será o responsável por tratar Ctrl+C.
        try:
            signal.signal(signal.SIGINT, signal.SIG_IGN)
        except Exception:
            # Em algumas plataformas (por ex. Windows) isto pode lançar; ignoramos.
            pass

        try:
            with open(self.outfile_path, 'a') as f:
                while not self.first_sub_names.empty():
                    try:
                        first = self.first_sub_names.get(timeout=0.1)
                    except Exception:
                        # timeout ou queue vazia momentânea
                        continue

                    sub1 = f"{first}.{self.target}"
                    self.print_testing(sub1)
                    try:
                        ips = self.resolve_fast(sub1)
                    except Exception as e:
                        # Prevent a DNS exception from killing the worker — log it and continue.
                        self.log_error(sub1, f"resolve_fast exception: {e}")
                        continue

                    if ips:
                        with self.subdomains_count.get_lock():
                            count = self.subdomains_count.value
                            self.subdomains_count.value += 1
                        self.print_valid(count, sub1, ips)
                        f.write(f"{sub1}\t{','.join(ips)}\n")
                        f.flush()

                        # Test second-level subdomains
                        for second in self.second_sub_names:
                            sub2 = f"{second}.{sub1}"
                            self.print_testing(sub2)
                            try:
                                ips2 = self.resolve_fast(sub2)
                            except Exception as e:
                                self.log_error(sub2, f"resolve_fast exception: {e}")
                                continue

                            if ips2:
                                with self.subdomains_count.get_lock():
                                    count = self.subdomains_count.value
                                    self.subdomains_count.value += 1
                                self.print_valid(count, sub2, ips2)
                                f.write(f"{sub2}\t{','.join(ips2)}\n")
                                f.flush()
        except KeyboardInterrupt:
            # Rare case: if we receive a local KeyboardInterrupt, terminate gracefully.
            return
        except Exception as e:
            # Regista erro inesperado e sai o worker
            self.log_error("scan_subdomains", f"Unhandled exception in worker: {e}")
            return

    def start_process(self):
        """
        Create workers and perform joins in short cycles
        to allow immediate capture of KeyboardInterrupt in the parent process.
        In case of Ctrl+C, terminate the child processes and exit.
        """
        processes = []
        try:
            for i in range(self.workers):
                process = Process(target=self.scan_subdomains, name=f"worker-{i}")
                process.daemon = False  # Keep as default; we will manage termination manually.
                process.start()
                processes.append(process)

            # Perform joins in a loop with a short timeout so that KeyboardInterrupt can be handled.
            while True:
                alive = [p for p in processes if p.is_alive()]
                if not alive:
                    break
                try:
                    for p in alive:
                        p.join(timeout=0.5)
                except KeyboardInterrupt:
                    # Caught Ctrl+C in the parent — terminating the child processes.
                    print(R + "\n[!] User forced interrupt! Terminating workers..." + W)
                    for pro in processes:
                        try:
                            if pro.is_alive():
                                pro.terminate()
                        except Exception:
                            pass
                    # dá um pequeno tempo para terminar e retorna erro
                    time.sleep(0.2)
                    # opcional: faz join definitivo para limpar
                    for pro in processes:
                        try:
                            pro.join(timeout=1.0)
                        except Exception:
                            pass
                    sys.exit(1)

        except KeyboardInterrupt:
            print(R + "\n[!] User forced interrupt!" + W)
            for pro in processes:
                try:
                    if pro.is_alive():
                        pro.terminate()
                except Exception:
                    pass
            time.sleep(0.1)
            sys.exit(1)
        except Exception as e:
            # loga e tenta terminar tudo
            print(R + f"\n[!] start_process unhandled exception: {e}" + W)
            for pro in processes:
                try:
                    if pro.is_alive():
                        pro.terminate()
                except Exception:
                    pass
            raise

# ----------------------------------------------------------------------------------------------------------

    def run(self):
        # Entry point to start scanning and handle keyboard interrupts gracefully
        try:
            self.start_process()
        except KeyboardInterrupt:
            #print(R + "\n[!] User forced interrupt!" + W)
            sys.exit(1)
        finally:
            with self.print_lock:
                # Clear spinner line before final results
                sys.stdout.write('\r' + ' ' * 80 + '\r')
                sys.stdout.flush()
            print(Y + f"\n[*] Total Subdomains Found: {self.subdomains_count.value}" + W)
            print(Y + f"[**] TugaRecon: Subdomains found in {time.time() - self.start:.2f} seconds" + W)
            print(Y + "\n[+] Output Result" + W)
            print(G + "**************************************************************" + W)
            print(R + "         ->->-> " + W, self.folder + "\n")
            sys.exit(0)
