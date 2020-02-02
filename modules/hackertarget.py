# TugaRecon - HackerTarget module, write by LordNeoStark
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By LordNeoStark | https://twitter.com/LordNeoStark | https://github.com/LordNeoStark
# import modules


import time
import requests

from functions import write_file
from functions import G, W

class Hackertarget:

    def __init__(self, target, output):

        self.target = target
        self.output = output
        self.module_name = "HackerTarget"
        self.engine = "hackertarget"

        print(G + f"HackerTarget: Enumerating subdomains now for {target} \n" + W)

        url = self.subdomains_list()
        self.enumerate(url, output)

    def subdomains_list(self):
        url = f"https://api.hackertarget.com/hostsearch/?q={self.target}"
        return url

    def enumerate(self, url, output):
        subdomains = set()
        subdomainscount = 0
        start_time = time.time()

        try:
            response = requests.get(url)

            while subdomainscount < 10000:

                # Remove "," an IP from list
                remove_ip = response.text.replace(",", " ")
                subdomains = remove_ip.split()

                subdomainscount = subdomainscount + 2
                print(f"[*] {subdomains[subdomainscount]}")

                # Write  to a file
                if self.output is not None:
                    write_file(subdomains[subdomainscount], self.engine + self.output)

            if self.output:
                print(f"\nSaving result... {self.engine + self.output}")

        except IndexError:
            pass

        print(G + f"\n[**] TugaRecon is complete.  HackerTarget: {int((subdomainscount/2)-1)} subdomains have been found in %s seconds" % (
                    time.time() - start_time) + W)

        if not subdomains:
            print(f"[x] No data found for {self.target} using  HackerTarget.")