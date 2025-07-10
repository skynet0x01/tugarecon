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

from multiprocessing import Queue, Process, freeze_support, Value, Lock
from utils.tuga_colors import G, Y, R, W


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
        # Try resolving domain using available DNS servers in round-robin
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
                resolver.resolve(domain, "A")
                return True  # Domain resolved successfully
            except Exception as e:
                self.log_error(domain, f"{e} (DNS {dns_server})")  # Log DNS errors silently
                continue
        
        return False  # Failed to resolve on all DNS servers
    
    def print_testing(self, domain):
        # Show rotating spinner with current testing domain on the same console line
        with self.print_lock:
            spinner_char = self.SPINNER[self.spinner_index % len(self.SPINNER)]
            self.spinner_index += 1
            msg = f"Testing {spinner_char} : {domain}"
            sys.stdout.write('\r' + msg.ljust(80))
            sys.stdout.flush()
    
    def print_valid(self, count, domain):
        # Clear spinner line and print a valid subdomain found with coloring
        with self.print_lock:
            sys.stdout.write('\r' + ' ' * 80 + '\r')  # Clear line
            print(f"{G}[*] {count}:   {domain}{W}")
            sys.stdout.flush()
    
    def log_error(self, domain, message):
        # Append DNS errors to a dedicated log file (thread/process safe)
        log_file = os.path.join(self.folder, "dns_errors.log")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.print_lock:  # avoid concurrent writes
            with open(log_file, 'a') as f:
                f.write(f"[{timestamp}] DNS Error for {domain}: {message}\n")
    
    def scan_subdomains(self):
        # Main scanning loop: dequeue first-level names, test them and then test second-level
        with open(self.outfile_path, 'a') as f:
            while not self.first_sub_names.empty():
                try:
                    first = self.first_sub_names.get(timeout=0.1)
                except:
                    continue
                
                sub1 = f"{first}.{self.target}"
                self.print_testing(sub1)
                if self.resolve_fast(sub1):
                    with self.subdomains_count.get_lock():
                        count = self.subdomains_count.value
                        self.subdomains_count.value += 1
                    self.print_valid(count, sub1)
                    f.write(sub1 + '\n')
                    f.flush()
                    
                    # Test second-level subdomains
                    for second in self.second_sub_names:
                        sub2 = f"{second}.{sub1}"
                        self.print_testing(sub2)
                        if self.resolve_fast(sub2):
                            with self.subdomains_count.get_lock():
                                count = self.subdomains_count.value
                                self.subdomains_count.value += 1
                            self.print_valid(count, sub2)
                            f.write(sub2 + '\n')
                            f.flush()
    
    def start_process(self):
        # Start multiprocessing worker processes to parallelize scanning
        processes = []
        try:
            for i in range(self.workers):
                process = Process(target=self.scan_subdomains, name=f"worker-{i}")
                process.start()
                processes.append(process)
            
            for process in processes:
                process.join()
        except KeyboardInterrupt:
            print(R + "\n[!] Interrupt detected. Terminating processes..." + W)
            for p in processes:
                p.terminate()
            for p in processes:
                p.join()
            sys.exit(1)
    
    def run(self):
        # Entry point to start scanning and handle keyboard interrupts gracefully
        try:
            self.start_process()
        except KeyboardInterrupt:
            print(R + "\n[!] User forced interrupt!" + W)
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

