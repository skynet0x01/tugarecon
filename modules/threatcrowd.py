# TugaRecon - threatcrowd, write by LordNeoStark
# import modules


import time
import requests

from functions import useragent
from functions import write_file
from functions import G, W

class Threatcrowd:

    def __init__(self, target, output):

        self.target = target
        self.output = output
        self.module_name = "Threat Crowd"
        self.engine = "threatcrowd"

        print(G + f"Threat Crowd: Enumerating subdomains now for {target} \n" + W)

        url = self.subdomains_list()
        self.enumerate(url, output)

    def subdomains_list(self):
        url = f'https://threatcrowd.org/searchApi/v2/domain/report/?domain={self.target}'
        return url

    def enumerate(self, url, output):
        subdomains = set()
        subdomainscount = 0
        start_time = time.time()

        try:
            response = requests.get(url, headers={'User-Agent': useragent()})

            while subdomainscount < 500:
                subdomains = response.json()["subdomains"][subdomainscount]
                subdomainscount = subdomainscount + 1
                print(f"[*] {subdomains}")

                if self.output is not None:
                    write_file(subdomains, self.engine + self.output)

            if self.output:
                print(f"\nSaving result... {self.engine + self.output}")

        except IndexError:
            pass

        print(G + f"\n[**] TugaRecon is complete. Threat Crowd: {subdomainscount} subdomains have been found in %s seconds" % (
                    time.time() - start_time) + W)

        if not subdomains:
            print(f"[x] No data found for {self.target} using Threat Crowd.")