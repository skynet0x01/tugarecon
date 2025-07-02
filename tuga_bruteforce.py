# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01

# import go here
# ----------------------------------------------------------------------------------------------------------
import os
import dns.resolver
import time
import datetime

from multiprocessing import Queue, Process, current_process, freeze_support, Value
from utils.tuga_colors import G, Y, R, W


class TugaBruteForce:
    def __init__(self, options):
        freeze_support()

        self.target = options.domain
        self.workers = options.threads
        self.options = options
        self.subdomains = ""
        self.first_wordlist = "wordlist/first_names.txt"
        self.second_wordlist = "wordlist/next_names.txt"
        self.start = time.time()
        self.first_sub_names = Queue()
        self.subdomains_count = Value('i', 0)

        # Load subdomain parts
        self.load_first_sub_names()
        self.second_sub_names = self.load_second_sub_names()

        # DNS setup
        self.dns_servers = self.load_dns_servers("dnslist/dns_servers.txt")
        self.primary_dns = self.get_first_working_dns()

        # Output setup
        self.date = str(datetime.datetime.now().date())
        pwd = os.getcwd()
        self.folder = os.path.join(pwd, "results/" + self.target + "/" + self.date)
        os.makedirs(self.folder, exist_ok=True)
        outfile = os.path.join(self.folder, "tuga_bruteforce.txt")
        self.outfile = open(outfile, 'w')

    def load_first_sub_names(self):
        with open(self.first_wordlist, 'r') as file:
            for linha in file:
                self.first_sub_names.put(linha.strip())

    def load_second_sub_names(self):
        with open(self.second_wordlist) as file:
            return [linha.strip() for linha in file]

    def load_dns_servers(self, filepath):
        servers = []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    servers.append(line)
        return servers

    def get_first_working_dns(self, test_domain="google.com"):
        for server in self.dns_servers:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [server]
            resolver.lifetime = 1.5
            try:
                resolver.resolve(test_domain, "A")
                return server
            except:
                continue
        return None

    def resolve_fast(self, domain):
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [self.primary_dns]
        resolver.lifetime = 1.5
        try:
            resolver.resolve(domain, "A")
            return True
        except:
            return False

    def scan_subdomains(self):
        processo = current_process().name

        while not self.first_sub_names.empty():
            try:
                elemento_first_sub_names = self.first_sub_names.get(timeout=0.1)
            except:
                continue

            sub_domain = elemento_first_sub_names + '.' + self.target
            if self.resolve_fast(sub_domain):
                with self.subdomains_count.get_lock():
                    count = self.subdomains_count.value
                    self.subdomains_count.value += 1
                print(f"     [*] {count}:   {sub_domain}", flush=True)
                self.outfile.write(sub_domain + '\n')
                self.outfile.flush()

                for second_sub in self.second_sub_names:
                    next_sub_domain = second_sub + '.' + sub_domain
                    if self.resolve_fast(next_sub_domain):
                        with self.subdomains_count.get_lock():
                            count = self.subdomains_count.value
                            self.subdomains_count.value += 1
                        print(f"     [*] {count}:   {next_sub_domain}", flush=True)
                        self.outfile.write(next_sub_domain + '\n')
                        self.outfile.flush()

    def start_process(self):
        processes = []
        for i in range(self.workers):
            process = Process(target=self.scan_subdomains, name=str(i))
            process.start()
            processes.append(process)

        for process in processes:
            process.join()

    def run(self):
        self.start_process()
        print(Y + f"\n[*] Total Subdomains Found: {self.subdomains_count.value}" + W)
        print(Y + f"[**]TugaRecon: Subdomains have been found in %s seconds" % (time.time() - self.start) + "\n" + W)
        print(Y + "\n[+] Output Result" + W)
        print(G + "**************************************************************" + W)
        print(R + "         ->->-> " + W, self.folder + "\n")