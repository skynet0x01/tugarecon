# TugaRecon - certspotter, write by LordNeoStark
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By LordNeoStark | https://twitter.com/LordNeoStark | https://github.com/LordNeoStark

# import modules
import time
import requests

from modules import tuga_useragents #random user-agent
from functions import write_file
from functions import DeleteDuplicate
from functions import G, W

class Certspotter:

    def __init__(self, target, output):

        self.target = target
        self.output = output
        self.module_name = "CertSpotter"
        self.engine = "certspotter"

        print(G + f"CertSpotter: Enumerating subdomains now for {target} \n" + W)

        self.response = self.engine_url()
        self.enumerate(self.response, output, target)
        if self.output is not None:
            DeleteDuplicate(self.engine + '_' + self.output, target)


    def engine_url(self):
        try:
            url = f'https://api.certspotter.com/v1/issuances?domain={self.target}&include_subdomains=true&expand=dns_names'
            response = requests.get(url, headers=tuga_useragents.useragent())
        except requests.exceptions.Timeout:
            pass
        return response

    def enumerate(self, response, output, target):
        subdomains = []
        subdomainscount = 0
        start_time = time.time()

        try:

            while subdomainscount < 100:
                subdomains = response.json()[subdomainscount]["dns_names"][0]
                subdomainscount = subdomainscount + 1
                print(f"[*] {subdomains}")

                if self.output is not None:
                    write_file(subdomains, self.engine + '_' + self.output, target)

            if self.output:
                print(f"\nSaving result... {self.engine + '_' + self.output}")

        except:
            pass

        if not subdomains:
            print(f"[x] No data found for {self.target} using CertSpotter.")
        else:
            print(G + f"\n[**] TugaRecon is complete. CertSpotter: {subdomainscount} subdomains have been found in %s seconds" % (
                    time.time() - start_time) + W)