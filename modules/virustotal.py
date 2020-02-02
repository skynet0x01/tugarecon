# TugaRecon - virustotal, write by LordNeoStark
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By LordNeoStark | https://twitter.com/LordNeoStark | https://github.com/LordNeoStark
# import modules

import time

import requests

from functions import G, W
from functions import useragent
from functions import write_file


class Virustotal:

    def __init__(self, target, output):

        self.target = target
        self.output = output
        self.module_name = "VirusTotal"
        self.engine = "Virustotal"

        print(G + f"VirusTotal: Enumerating subdomains now for {target} \n" + W)

        url = self.subdomains_list()
        self.enumerate(url, output)

    def subdomains_list(self):
        url = f'https://www.virustotal.com/ui/domains/{self.target}/subdomains?limit=40'
        return url

    def enumerate(self, url, output):
        subdomains = set()
        subdomainscount = 0
        start_time = time.time()

        try:
            response = requests.get(url, headers={'User-Agent': useragent()})

            while subdomainscount < 40:
                subdomains = response.json()["data"][subdomainscount]["id"]
                subdomainscount = subdomainscount + 1
                print(f"[*] {subdomains}")

                if self.output is not None:
                    write_file(subdomains, self.engine + self.output)

            if self.output:
                print(f"\nSaving result... {self.engine + self.output}")

        except IndexError:
            pass

        print(
            G + f"\n[**] TugaRecon is complete. VirusTotal: {subdomainscount} subdomains have been found in %s seconds" % (
                    time.time() - start_time) + W)

        if not subdomains:
            print(f"[x] No data found for {self.target} using VirusTotal.")
