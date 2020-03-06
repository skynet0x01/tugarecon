# TugaRecon, tribute to Portuguese explorers reminding glorious past of this country
# Bug Bounty Recon, search for subdomains and save in to a file
# Coded By LordNeoStark | https://twitter.com/LordNeoStark | https://github.com/LordNeoStark

# import go here

import sys
import requests
import time
import re

from functions import G, W
from modules import tuga_useragents
from functions import write_file

class Entrust:

    def __init__(self, target, output):

        self.target = target
        self.output = output
        self.module_name = "Entrust Datacard"
        self.engine = "entrust"

        requests.packages.urllib3.disable_warnings()

        print(G + f"Entrust Datacard: Enumerating subdomains now for {target} \n" + W)

        print("[+]: Downloading domain list...")
        self.response = self.engine_url(target)
        print("[+]: Download complete.")
        self.domains = self.enumerate(self.response)
        print("[+]: Parsed %s domain(s) from list." % len(self.domains))

        print("\n[+]: Domains found...")
        self.printDomains(self.domains, self.target, self.output)

    def engine_url(self, target):
        url = f'https://ctsearch.entrust.com/api/v1/certificates?fields=subjectDN&domain={self.target}&includeExpired=true&exactMatch=false&limit=5000'
        response = requests.get(url, headers=tuga_useragents.useragent(), verify = False)
        return response

    def enumerate(self, response):
        domains = []
        start_time = time.time()

        restring = re.compile(r"cn\\u003d(.*?)(\"|,)", re.MULTILINE)
        match = re.findall(restring, response.text)

        if match:
            for domain in match:
                # The following line avoids adding wildcard domains, as they will not resolve.
                if ((domain[0] not in domains) and not (re.search("^\*\.", domain[0]))):
                    domains.append(domain[0])
        return domains

    def printDomains(self, domains, target, output):
        for domain in sorted(domains):
            print(domain)

            if self.output is not None:
                write_file(domain, self.engine + '_' + self.output, target)

        if self.output:
            print(f"\nSaving result... {self.engine + '_' + self.output}")



#########################################################################################################