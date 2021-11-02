# TugaRecon - crt module, write by skynet0x01
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01
# import modules
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
class CRT:

    def __init__(self, target, output):

        self.target = target
        self.output = output
        self.module_name = "SSL Certificates"
        self.engine = "crt"
        self.response = self.engine_url() # URL

        print(G + f"SSL Certificates: Enumerating subdomains now for {target} \n" + W)
        self.enumerate(self.response, output, target) # Call the function enumerate

        if self.output is not None and self.subdomainscount != 0:
            DeleteDuplicate(self.engine + '_' + self.output, target)
        else:
            pass
################################################################################
    def engine_url(self):
        try:
            url = f"https://crt.sh/?q={self.target}&output=json"
            response = requests.get(url, headers=tuga_useragents.useragent())
            return response
        except requests.ConnectionError:
            print(G + f"SSL: Warning! Unable to get subdomains... Try again!\n" + W)
            exit(1)
################################################################################
    def enumerate(self, response, output, target):
        subdomains = set()
        self.subdomainscount = 0
        start_time = time.time()
        try:
            while self.subdomainscount < 10000:
                subdomains = response.json()[self.subdomainscount]["name_value"]
                if not subdomains:
                    print(f"[x] Oops! No data found for {self.target} using  SSL Certificates.")
                else:
                    self.subdomainscount = self.subdomainscount + 1
                    if "@" in subdomains:  # filter for emails
                        pass
                    else:
                        print(f"[*] {subdomains}")
                        if self.output is not None:
                            write_file(subdomains, self.engine + '_' + self.output, target)
            if self.output:
                print(f"\nSaving result... {self.engine + '_'+ self.output}")
        except IndexError:
            pass
            print(
                G + f"\n[**] TugaRecon is complete.  SSL Certificates: {self.subdomainscount} subdomains have been found in %s seconds" % (
                        time.time() - start_time) + W)
