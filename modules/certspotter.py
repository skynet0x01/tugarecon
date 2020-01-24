# TugaRecon - certspotter, write by LordNeoStark
# import modules
import time
import requests

from functions import useragent
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
        self.enumerate(url, output)

    def subdomains_list(self):
        url = f'https://api.certspotter.com/v1/issuances?domain={self.target}&include_subdomains=true&expand=dns_names'
        return url

    def enumerate(self, url, output):
        subdomains = set()
        subdomainscount = 0
        start_time = time.time()

        try:
            response = requests.get(url, headers={'User-Agent': useragent()})

            while subdomainscount < 100:
                subdomains = response.json()[subdomainscount]["dns_names"][0]
                subdomainscount = subdomainscount + 1
                print(f"[*] {subdomains}")

                if self.output is not None:
                    write_file(subdomains, self.engine + self.output)

            if self.output:
                print(f"\nSaving result... {self.engine + self.output}")

        except IndexError:
            pass

        print(G + f"\n[**] TugaRecon is complete. CertSpotter: {subdomainscount} subdomains have been found in %s seconds" % (
                    time.time() - start_time) + W)

        if not subdomains:
            print(f"[x] No data found for {target} using CertSpotter.")