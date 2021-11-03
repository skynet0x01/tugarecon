# TugaRecon - threatcrowd, write by skynet0x01
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01
# import modules
################################################################################
import time
import requests
import json
# Import internal modules
from modules import tuga_useragents #random user-agent
# Import internal functions
from functions import write_file
from functions import DeleteDuplicate
from functions import G, W
################################################################################
class Threatcrowd:

    def __init__(self, target, output):

        self.target = target
        self.output = output
        self.module_name = "Threat Crowd"
        self.engine = "threatcrowd"
        self.response = self.engine_url()

        if self.response != 1:
            print(G + f"\nThreatCrowd: Enumerating subdomains now for {target} \n" + W)
            self.enumerate(self.response, output, target) # Call the function enumerate
        else:
            pass
        if self.output is not None:
            DeleteDuplicate(self.engine + '_' + self.output, target)
################################################################################
    def engine_url(self):
        try:
            url = f'https://threatcrowd.org/searchApi/v2/domain/report/?domain={self.target}'
            response = requests.get(url, headers=tuga_useragents.useragent())
            return response
        except requests.ConnectionError:
            print(G + f"[Threat Crowd] Warning! Unable to get subdomains... Try again!\n" + W)
            response = 1
            return response
################################################################################
    def enumerate(self, response, output, target):
        subdomains = set()
        subdomainscount = 0
        start_time = time.time()
        try:
            #Test json
            subdomains = response.json()["subdomains"][subdomainscount]
        except KeyError:
            print(G + f"[x] Decoding JSON has failed.... No data found for {self.target} using Threat Crowd." + W)
            exit(1)
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
        print(G + f"\n[**]Threat Crowd: {subdomainscount} subdomains have been found in %s seconds" % (
                    time.time() - start_time) + W)
        if not subdomains:
            print(f"[x] No data found for {self.target} using Threat Crowd.")
