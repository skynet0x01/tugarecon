# TugaRecon - threatcrowd, write by LordNeoStark
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By LordNeoStark | https://twitter.com/LordNeoStark | https://github.com/LordNeoStark
# import modules


import time
import requests

from modules import tuga_useragents
from functions import write_file
from functions import DeleteDuplicate
from functions import G, W

class Threatcrowd:

    def __init__(self, target, output):

        self.target = target
        self.output = output
        self.module_name = "Threat Crowd"
        self.engine = "threatcrowd"

        print(G + f"Threat Crowd: Enumerating subdomains now for {target} \n" + W)

        self.response = self.engine_url()
        self.enumerate(self.response, output, target)
        if self.output is not None:
            DeleteDuplicate(self.engine + '_' + self.output, target)


    def engine_url(self):
        try:
            url = f'https://threatcrowd.org/searchApi/v2/domain/report/?domain={self.target}'
            response = requests.get(url, headers=tuga_useragents.useragent())
        except requests.exceptions.Timeout:
            pass
        return response

    def enumerate(self, response, output, target):
        subdomains = set()
        subdomainscount = 0
        start_time = time.time()

        try:
            while subdomainscount < 500:
                subdomains = response.json()["subdomains"][subdomainscount]
                subdomainscount = subdomainscount + 1
                print(f"[*] {subdomains}")

                if self.output is not None:
                    write_file(subdomains, self.engine + '_' + self.output, target)

            if self.output:
                print(f"\nSaving result... {self.engine + '_' + self.output}")

        except IndexError:
            pass

        print(G + f"\n[**] TugaRecon is complete. Threat Crowd: {subdomainscount} subdomains have been found in %s seconds" % (
                    time.time() - start_time) + W)

        if not subdomains:
            print(f"[x] No data found for {self.target} using Threat Crowd.")