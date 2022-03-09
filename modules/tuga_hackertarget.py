# TugaRecon - HackerTarget module, write by skynet0x01
# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By skynet0x01
# import modules
################################################################################
import time
import requests
# Import internal modules
from modules import tuga_useragents #random user-agent
# Import internal functions
from functions import write_file
from functions import DeleteDuplicate
from functions import G, W
################################################################################
class Hackertarget:

    def __init__(self, target, output):

        self.target = target
        self.output = output
        self.module_name = "HackerTarget"
        self.engine = "hackertarget"
        self.response = self.engine_url()

        if self.response != 1:
            print(G + f"\nHackerTarget: Enumerating subdomains now for {target} \n" + W)
            self.enumerate(self.response, output, target) # Call the function enumerate
        else:
            pass
        #if self.output is not None and int((subdomainscount / 2) - 1) != 0:
        #    DeleteDuplicate(self.engine + '_' + self.output, target)
################################################################################
    def engine_url(self):
        try:
            url = f"https://api.hackertarget.com/hostsearch/?q={self.target}"
            response = requests.get(url, headers=tuga_useragents.useragent())
            return response
        except requests.ConnectionError:
            print(G + f"[HackerTarget] Warning! Unable to get subdomains... Try again!\n" + W)
            response = 1
            return response
################################################################################
    def enumerate(self, response, output, target):
        subdomains = []
        subdomainscount = 0
        sub = []
        start_time = time.time()
        #################################
        try:
            while subdomainscount < 10000:
                # Remove "," an IP from list
                remove_ip = response.text.replace(",", " ")
                subdomains = remove_ip.split()
                # Print subdomains...
                subdomainscount = subdomainscount + 2
                print(f"[*] {subdomains[subdomainscount]}")
                # Write  to a file
                if self.output is not None and int((subdomainscount / 2) - 1) != 0:
                    write_file(subdomains[subdomainscount], self.engine + '_' + self.output, target)
                else:
                    pass
        except IndexError:
            pass
        #################################
        if self.output and not subdomains:
            print(f"\nSaving result... {self.engine + '_' + self.output}")
        if not subdomains:
            print(f"[x] No data found for {self.target} using  HackerTarget.\n")
        else:
            print(G + f"\n[**]HackerTarget: {int((subdomainscount / 2) - 1)} subdomains have been found in %s seconds" % (time.time() - start_time) +"\n"+ W)
            if self.output is not None and int((subdomainscount / 2) - 1) != 0:
                DeleteDuplicate(self.engine + '_' + self.output, target)
            else:
                pass
