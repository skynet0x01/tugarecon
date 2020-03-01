# TugaRecon - certspotter, write by LordNeoStark
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By LordNeoStark | https://twitter.com/LordNeoStark | https://github.com/LordNeoStark

# import modules
import time
import requests

from modules import tuga_useragents #random user-agent
from functions import write_file
from functions import G, W

class Certspotter:

    def __init__(self, target, output):

        self.target = target
        self.output = output
        self.module_name = "CertSpotter"
        self.engine = "certspotter"

        print(G + f"CertSpotter: Enumerating subdomains now for {target} \n" + W)

        url = self.subdomains_list()
        self.enumerate(url, output, target)

    def subdomains_list(self):
        url = f'https://api.certspotter.com/v1/issuances?domain={self.target}&include_subdomains=true&expand=dns_names'
        return url

    def enumerate(self, url, output, target):
        subdomains = set()
        subdomainscount = 0
        start_time = time.time()

        try:
            response = requests.get(url, headers=tuga_useragents.useragent())

            while subdomainscount < 100:
                subdomains = response.json()[subdomainscount]["dns_names"][0]
                subdomainscount = subdomainscount + 1
                print(f"[*] {subdomains}")

                if self.output is not None:
                    write_file(subdomains, self.engine + '_' + self.output, target)

            if self.output:
                print(f"\nSaving result... {self.engine + '_' + self.output}")

        except IndexError:
            pass

        print(G + f"\n[**] TugaRecon is complete. CertSpotter: {subdomainscount} subdomains have been found in %s seconds" % (
                    time.time() - start_time) + W)

        if not subdomains:
            print(f"[x] No data found for {self.target} using CertSpotter.")